import flet as ft
import requests

BASE_URL = "http://192.168.1.83:5002"  # IP da sua API


def main(page: ft.Page):
    page.title = "SmartSell"
    # Guarda token e user completo (incluindo id) na sessão
    page.session.set("token", None)
    page.session.set("user", None)

    def api_request(method, endpoint, data=None):
        headers = {}
        token = page.session.get("token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        url = f"{BASE_URL}{endpoint}"
        try:
            r = requests.request(method, url, json=data, headers=headers, timeout=8)
            try:
                return r.status_code, r.json()
            except:
                return r.status_code, {"msg": r.text}
        except requests.exceptions.RequestException as e:
            return 0, {"msg": f"Erro de conexão: {e}"}

    # ---------------- VIEWS ----------------
    def login_view():
        email = ft.TextField(label="Email")
        senha = ft.TextField(label="Senha", password=True, can_reveal_password=True)

        def do_login(e):
            status, res = api_request("POST", "/login", {
                "email": email.value,
                "senha": senha.value
            })
            if status == 200:
                page.session.set("token", res["access_token"])
                # agora pedimos /me para obter id e demais infos
                st, rme = api_request("GET", "/me")
                if st == 200:
                    page.session.set("user", rme)
                else:
                    # se falhar, guarda pelo menos nome/email do login
                    page.session.set("user", {"nome": res.get("nome"), "email": email.value})
                page.snack_bar = ft.SnackBar(ft.Text("Login realizado!"), open=True)
                page.update()
                go_menu()
            else:
                page.snack_bar = ft.SnackBar(ft.Text(res.get("msg", "Credenciais inválidas")), open=True)
                page.update()

        return ft.View(
            "/login",
            controls=[
                ft.AppBar(title=ft.Text("Login")),
                ft.Column([email, senha, ft.ElevatedButton("Entrar", on_click=do_login),
                           ft.TextButton("Não tem conta? Cadastre-se", on_click=lambda _: go_cadastro())],
                          alignment="center", horizontal_alignment="center", width=400)
            ]
        )

    def cadastro_view():
        nome = ft.TextField(label="Nome")
        telefone = ft.TextField(label="Telefone")
        email = ft.TextField(label="Email")
        senha = ft.TextField(label="Senha", password=True, can_reveal_password=True)

        def do_cadastro(e):
            status, res = api_request("POST", "/cadastro/usuario", {
                "nome": nome.value,
                "telefone": telefone.value,
                "email": email.value,
                "senha": senha.value
            })
            if status == 201:
                page.snack_bar = ft.SnackBar(ft.Text("Cadastro realizado! Faça login."), open=True)
                page.update()
                go_login()
            else:
                page.snack_bar = ft.SnackBar(ft.Text(res.get("msg", "Erro no cadastro")), open=True)
                page.update()

        return ft.View(
            "/cadastro",
            controls=[
                ft.AppBar(title=ft.Text("Cadastro")),
                ft.Column([nome, telefone, email, senha, ft.ElevatedButton("Cadastrar", on_click=do_cadastro),
                           ft.TextButton("Já tem conta? Login", on_click=lambda _: go_login())],
                          alignment="center", horizontal_alignment="center", width=500)
            ]
        )

    def menu_view():
        user = page.session.get("user") or {}
        bem = f"Bem-vindo, {user.get('nome','Usuário')}!"
        # opcional: mostrar mais vendido (pode adicionar endpoint no backend para isso)
        return ft.View(
            "/menu",
            controls=[
                ft.AppBar(title=ft.Text("Menu Principal")),
                ft.Column([
                    ft.Text(bem, size=20, weight="bold"),
                    ft.ElevatedButton("Cardápio", on_click=lambda _: go_cardapio()),
                    ft.ElevatedButton("Pedidos", on_click=lambda _: go_pedidos()),
                    ft.ElevatedButton("Editar Usuário", on_click=lambda _: go_editar_usuario()),
                    ft.ElevatedButton("Sair", on_click=lambda _: do_logout())
                ], alignment="center", horizontal_alignment="center")
            ]
        )

    def cardapio_view():
        st, res = api_request("GET", "/cardapio")
        itens = res.get("cardapio", []) if st == 200 else []

        lista = []
        for item in itens:
            # criar handler com closure para capturar item id correto
            def make_handler(pid):
                return lambda e: go_comprar(pid)
            lista.append(
                ft.Card(
                    ft.Container(
                        ft.Row([
                            ft.Column([ft.Text(item["nome"], weight="bold"), ft.Text(item.get("descricao",""))]),
                            ft.Column([ft.Text(f"R$ {item.get('preco',0):.2f}"),
                                       ft.ElevatedButton("Comprar", on_click=make_handler(item["id"]))])
                        ], alignment="spaceBetween"),
                        padding=12
                    )
                )
            )

        def show_promocao(e):
            page.snack_bar = ft.SnackBar(ft.Text("Nenhuma promoção ativa"), open=True)
            page.update()

        return ft.View(
            "/cardapio",
            controls=[
                ft.AppBar(title=ft.Text("Cardápio")),
                ft.Column(lista) if lista else ft.Column([ft.Text("Nenhum item no cardápio.")]),
                ft.Row([ft.ElevatedButton("Promoções", on_click=show_promocao),
                        ft.TextButton("Voltar", on_click=lambda _: go_menu())], alignment="center")
            ]
        )

    def pedidos_view():
        st, res = api_request("GET", "/pedido")
        pedidos = res.get("pedidos", []) if st == 200 else []

        lista = []
        for p in pedidos:
            lista.append(
                ft.Card(
                    ft.Container(
                        ft.Column([
                            ft.Text(f"Pedido #{p['id']} - Produto: {p.get('produto')}"),
                            ft.Text(f"Quantidade: {p['quantidade']}  -  Total: R$ {p['valor_total']:.2f}"),
                            ft.Text(f"Status: {p['status']}  -  Data: {p['data']}")
                        ]),
                        padding=10
                    )
                )
            )

        return ft.View(
            "/pedidos",
            controls=[
                ft.AppBar(title=ft.Text("Meus Pedidos")),
                ft.Column(lista) if lista else ft.Text("Nenhum pedido realizado."),
                ft.TextButton("Voltar", on_click=lambda _: go_menu())
            ]
        )

    def editar_usuario_view():
        user = page.session.get("user") or {}
        nome = ft.TextField(label="Nome", value=user.get("nome",""))
        telefone = ft.TextField(label="Telefone", value=user.get("telefone",""))
        email = ft.TextField(label="Email", value=user.get("email",""))
        senha = ft.TextField(label="Senha (deixe vazio se não trocar)", password=True, can_reveal_password=True)

        def salvar(e):
            payload = {
                "nome": nome.value,
                "telefone": telefone.value,
                "email": email.value
            }
            if senha.value and senha.value.strip():
                payload["senha"] = senha.value.strip()

            st, res = api_request("PUT", "/editar/usuario", payload)
            if st == 200:
                # atualiza sessão com o objeto retornado (res["usuario"])
                page.session.set("user", res.get("usuario", payload))
                page.snack_bar = ft.SnackBar(ft.Text("Dados atualizados com sucesso!"), open=True)
            else:
                page.snack_bar = ft.SnackBar(ft.Text(res.get("msg", "Erro ao atualizar")), open=True)
            page.update()

        return ft.View(
            "/editar_usuario",
            controls=[
                ft.AppBar(title=ft.Text("Editar Usuário")),
                ft.Column([nome, telefone, email, senha, ft.ElevatedButton("Salvar", on_click=salvar),
                           ft.TextButton("Voltar", on_click=lambda _: go_menu())], alignment="center")
            ]
        )

    def comprar_view(item_id):
        quantidade = ft.TextField(label="Quantidade", value="1")

        def confirmar(e):
            try:
                qtd = int(quantidade.value)
                if qtd <= 0:
                    qtd = 1
            except:
                qtd = 1

            st, res = api_request("POST", "/pedido", {
                "produto_id": item_id,
                "quantidade": qtd
            })
            if st in (200, 201):
                page.snack_bar = ft.SnackBar(ft.Text("Pedido realizado com sucesso!"), open=True)
                page.update()
                go_pedidos()
            else:
                page.snack_bar = ft.SnackBar(ft.Text(res.get("msg", "Erro ao efetuar pedido")), open=True)
                page.update()

        return ft.View(
            f"/comprar/{item_id}",
            controls=[
                ft.AppBar(title=ft.Text("Comprar Produto")),
                ft.Column([ft.Text(f"Confirmar compra do produto ID {item_id}"), quantidade,
                           ft.ElevatedButton("Confirmar Compra", on_click=confirmar),
                           ft.TextButton("Voltar", on_click=lambda _: go_cardapio())], alignment="center")
            ]
        )

    # ---------- helpers de navegação ----------
    def do_logout():
        page.session.set("token", None)
        page.session.set("user", None)
        page.snack_bar = ft.SnackBar(ft.Text("Desconectado"), open=True)
        page.update()
        go_login()

    def go_login(): page.go("/login")
    def go_cadastro(): page.go("/cadastro")
    def go_menu(): page.go("/menu")
    def go_cardapio(): page.go("/cardapio")
    def go_pedidos(): page.go("/pedidos")
    def go_editar_usuario(): page.go("/editar_usuario")
    def go_comprar(pid): page.go(f"/comprar/{pid}")

    def route_change(e):
        route = page.route
        page.views.clear()
        if route == "/login":
            page.views.append(login_view())
        elif route == "/cadastro":
            page.views.append(cadastro_view())
        elif route == "/menu":
            page.views.append(menu_view())
        elif route == "/cardapio":
            page.views.append(cardapio_view())
        elif route == "/pedidos":
            page.views.append(pedidos_view())
        elif route == "/editar_usuario":
            page.views.append(editar_usuario_view())
        elif route.startswith("/comprar/"):
            pid = int(route.split("/")[-1])
            page.views.append(comprar_view(pid))
        page.update()

    page.on_route_change = route_change
    page.go("/login")


ft.app(target=main)
