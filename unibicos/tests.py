from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status

from unibicos.models import Categorias, Usuario, InstituicoesEnsino, Lojas


class ProdutoTestCase(APITestCase):
    def setUp(self):
        # usuário
        self.user = User.objects.create_user(username="test", password="123456")

        # pega token JWT
        response = self.client.post("/api/token/", {"username": "test", "password": "123456"})

        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        # instituição
        self.inst = InstituicoesEnsino.objects.create(
            nome="UFAL",
            sigla="UFAL",
            campus="A.C. Simões",
            cidade="Maceió",
            estado="AL",
            id_user_cad=self.user,
        )

        # usuario
        self.usuario = Usuario.objects.create(
            user=self.user,
            id_instituicao=self.inst,
            nome="Teste",
            telefone="82999999999",
            cpf="12345678901",
            id_user_cad=self.user,
        )

        # categoria
        self.categoria = Categorias.objects.create(
            nome_categoria="Salgados", icon="food", id_user_cad=self.user
        )

        # loja
        self.loja = Lojas.objects.create(
            id_usuario=self.usuario,
            nome_fantasia="Loja Teste",
            info_bancarias="123",
            localizacao="UFAL",
            id_user_cad=self.user,
        )

    def test_criar_produto(self):
        imagem = SimpleUploadedFile(
            name="test.jpg", content=b"file_content", content_type="image/jpeg"
        )

        data = {
            "nome": "Coxinha",
            "descricao": "Top",
            "preco": 10,
            "id_loja": self.loja.id_loja,
            "id_categoria": self.categoria.id_categoria,
            "disponivel": True,
            "imagem": imagem,
        }

        response = self.client.post("/api/produtos/", data, format="multipart")

        print(response.data)  # debug

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_listar_produtos(self):
        response = self.client.get("/api/produtos/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sem_token(self):
        self.client.credentials()  # remove token
        response = self.client.get("/api/produtos/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
