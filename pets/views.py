from rest_framework.views import APIView, Request, Response, status

from groups.models import Group
from pets.serializers import PetSerializer
from traits.models import Trait

from .models import Pet
from rest_framework.pagination import PageNumberPagination


class PetsView(APIView, PageNumberPagination):
    def get(self, request: Request) -> Response:
        trait_param = request.query_params.get('trait')
        pets = Pet.objects.all()

        if trait_param:
            pets = pets.filter(traits__name=trait_param)

        result_page = self.paginate_queryset(pets, request)
        serializer = PetSerializer(instance=result_page, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = PetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group_list = serializer.validated_data.pop("group")
        trait_list = serializer.validated_data.pop("traits")

        group_obj = Group.objects.filter(
            scientific_name__iexact=group_list["scientific_name"]).first()
        if not group_obj:
            group_obj = Group.objects.create(**group_list)

        pet = Pet.objects.create(**serializer.validated_data, group=group_obj)

        for trait in trait_list:
            trait_obj = Trait.objects.filter(name__iexact=trait["name"]).first()
            if not trait_obj:
                trait_obj = Trait.objects.create(**trait)

            pet.traits.add(trait_obj)

        pet.save()
        serializer = PetSerializer(instance=pet)

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class PetsDetailsView(APIView):
    def get(self, request: Request, pet_id: int) -> Response:
        try:
            pet = Pet.objects.get(id=pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PetSerializer(instance=pet)
        return Response(serializer.data)

    def delete(self, request: Request, pet_id: int) -> Response:
        try:
            pet = Pet.objects.get(id=pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        pet.delete()
        return Response(status=204)

    def patch(self, request: Request, pet_id: int) -> Response:
        try:
            pet = Pet.objects.get(id=pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PetSerializer(data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # terminar a logica
        group = serializer.validated_data.pop("group", None)
        traits = serializer.validated_data.pop("traits", None)

        if group:
            try:
                new_group = Group.objects.get(
                    scientific_name__iexact=group["scientific_name"]
                )
                pet.group = new_group
            except Group.DoesNotExist:
                group = Group.objects.create(**group)
                pet.group = group

        if traits:
            for trait in traits:
                trait_obj = Trait.objects.filter(name__iexact=trait["name"]).first()
                if not trait_obj:
                    trait_obj = Trait.objects.create(**trait)
                pet.traits.add(trait_obj)
                new_group = Group

        for key, value in serializer.validated_data.items():
            setattr(pet, key, value)

        pet.save()
        serializer = PetSerializer(pet)

        return Response(serializer.data, status=status.HTTP_200_OK)
