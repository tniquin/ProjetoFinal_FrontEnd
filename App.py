import flet as ft
import requests

BASE_URL = "http://192.168.1.83:5002"


def main(page: ft.Page):
    page.title = "SmartSell"
    page.session.set("token", None)
    page.session.set("user", None)
    page.window.height = 800
    page.window.width = 378

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
        email = ft.TextField(
            label="EMAIL",
            prefix_icon=ft.Icons.LOCK,
            border_color=ft.Colors.AMBER,
            border_radius=10,
            focused_border_color=ft.Colors.AMBER,
            width=300,
            color = ft.Colors.BLACK
        )

        senha = ft.TextField(
            label="SENHA",
            prefix_icon=ft.Icons.PERSON,
            password=True,
            can_reveal_password=True,
            border_color=ft.Colors.AMBER,
            border_radius=10,
            focused_border_color=ft.Colors.AMBER,
            width=300,
            color = ft.Colors.BLACK
        )
        def do_login(e):
            status, res = api_request("POST", "/login", {
                "email": email.value,
                "senha": senha.value
            })
            if status == 200:
                page.session.set("token", res["access_token"])
                st, rme = api_request("GET", "/me")
                if st == 200:
                    page.session.set("user", rme)
                else:
                    page.session.set("user", {"nome": res.get("nome"), "email": email.value})
                page.snack_bar = ft.SnackBar(ft.Text("Login realizado!"), open=True)
                page.update()
                go_menu()
            else:
                page.snack_bar = ft.SnackBar(ft.Text(res.get("msg", "Credenciais inválidas")), open=True)
                page.update()

        return ft.View(
            "/login",
            bgcolor=ft.Colors.AMBER_50,
            controls=[
                ft.Container(
                    expand=True,
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        [
                            ft.Icon(
                                ft.Icons.ACCOUNT_CIRCLE,
                                size=120,
                                color=ft.Colors.RED
                            ),
                            email,
                            senha,
                            ft.ElevatedButton(
                                "ENTRAR",
                                on_click=do_login,
                                bgcolor=ft.Colors.RED,
                                color=ft.Colors.WHITE,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=20),
                                    padding=20
                                ),
                                width=150
                            ),
                            ft.Text(
                                "NOVO USUÁRIO?\nENTÃO",
                                size=14,
                                weight="bold",
                                text_align="center",
                                color=ft.Colors.BLACK,
                                spans=[
                                    ft.TextSpan(
                                        " CADASTRE-SE",
                                        ft.TextStyle(color=ft.Colors.RED),
                                        on_click=lambda _: go_cadastro()  # <<< aqui troca de rota
                                    )
                                ]
                            ),
                        ],
                        alignment="center",
                        horizontal_alignment="center",
                        spacing=25
                    )
                )
            ]
        )

    def cadastro_view():
        nome = ft.TextField(
            label="NOME",
            label_style=ft.TextStyle( weight="bold"),
            prefix_icon=ft.Icons.PERSON,
            border_color=ft.Colors.AMBER,
            border_radius=10,
            focused_border_color=ft.Colors.AMBER,
            color=ft.Colors.BLACK,
            width=300
        )

        email = ft.TextField(
            label="EMAIL",
            label_style=ft.TextStyle( weight="bold"),
            prefix_icon=ft.Icons.LOCK,
            border_color=ft.Colors.AMBER,
            border_radius=10,
            focused_border_color=ft.Colors.AMBER,
            color=ft.Colors.BLACK,
            width=300
        )

        telefone = ft.TextField(
            label="TELEFONE",
            label_style=ft.TextStyle( weight="bold"),
            prefix_icon=ft.Icons.PHONE,
            border_color=ft.Colors.AMBER,
            border_radius=10,
            focused_border_color=ft.Colors.AMBER,
            color=ft.Colors.BLACK,
            width=300
        )

        senha = ft.TextField(
            label="SENHA",
            label_style=ft.TextStyle( weight="bold"),
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            border_color=ft.Colors.AMBER,
            border_radius=10,
            focused_border_color=ft.Colors.AMBER,
            color=ft.Colors.BLACK,
            width=300
        )
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
            bgcolor=ft.Colors.AMBER_50,
            controls=[
                ft.Container(
                    expand=True,
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        [
                            # Ícone topo
                            ft.Icon(
                                ft.Icons.ACCOUNT_CIRCLE,
                                size=120,
                                color=ft.Colors.RED
                            ),

                            # Campos
                            nome,
                            email,
                            telefone,
                            senha,

                            # Texto "já tem uma conta? entre agora"
                            ft.Text(
                                spans=[
                                    ft.TextSpan("JÁ TEM UMA CONTA?",
                                                ft.TextStyle(color=ft.Colors.BLACK, weight="bold")),
                                    ft.TextSpan(" "),
                                    ft.TextSpan(
                                        "ENTRE AGORA",
                                        ft.TextStyle(color=ft.Colors.RED, weight="bold"),
                                        on_click=lambda _: go_login()
                                    )
                                ],
                                text_align="center"
                            ),

                            # Botão Criar
                            ft.ElevatedButton(
                                "CRIAR",
                                on_click=do_cadastro,
                                bgcolor=ft.Colors.RED,
                                color=ft.Colors.WHITE,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=20),
                                    padding=20
                                ),
                                width=150
                            ),
                        ],
                        alignment="center",
                        horizontal_alignment="center",
                        spacing=20
                    )
                )
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
