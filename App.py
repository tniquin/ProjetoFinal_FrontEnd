import flet as ft
import requests
from datetime import datetime

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
        email = ft.TextField(label="Email")
        senha = ft.TextField(label="Senha", password=True, can_reveal_password=True)

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
                page.update()
                go_menu()
            else:
                page.update()

        return ft.View(
            "/login",
            controls=[
                ft.Column(
                    [
                        email,
                        senha,
                        ft.ElevatedButton("Entrar", on_click=do_login),
                        ft.TextButton("Cadastrar-se", on_click=lambda _: go_cadastro()),
                    ],
                    alignment="center",
                    horizontal_alignment="center",
                    expand=True
                )
            ]
        )

    def cadastro_view():
        nome = ft.TextField(label="Nome")
        email = ft.TextField(label="Email")
        telefone = ft.TextField(label="Telefone")
        senha = ft.TextField(label="Senha", password=True, can_reveal_password=True)

        def do_cadastro(e):
            status, res = api_request("POST", "/cadastro/usuario", {
                "nome": nome.value,
                "telefone": telefone.value,
                "email": email.value,
                "senha": senha.value
            })
            if status == 201:
                go_login()
            else:
                page.update()

        return ft.View(
            "/cadastro",
            controls=[
                ft.Column(
                    [
                        nome,
                        email,
                        telefone,
                        senha,
                        ft.ElevatedButton("Criar Conta", on_click=do_cadastro),
                        ft.TextButton("Já tem conta? Entrar", on_click=lambda _: go_login())
                    ],
                    alignment="center",
                    horizontal_alignment="center",
                    expand=True
                )
            ]
        )

    def menu_view():
        user = page.session.get("user") or {}
        nome = user.get("nome", "Usuário")


        return ft.View(
            "/menu",
            controls=[
                ft.Text(f"Bem-vindo, {nome}!"),
                ft.Column(
                    [
                        ft.TextButton("Cardápio", on_click=lambda _: go_cardapio()),
                        ft.TextButton("Carrinho", on_click=lambda _: go_carrinho()),
                        ft.TextButton("Meus Pedidos", on_click=lambda _: go_pedidos()),
                        ft.TextButton("Editar Usuário", on_click=lambda _: go_editar_usuario()),
                        ft.TextButton("Sair", on_click=lambda _: do_logout())
                    ],
                    alignment="center",
                    horizontal_alignment="center"
                )
            ]
        )

    def cardapio_view():
        st, res = api_request("GET", "/cardapio")
        itens = res.get("cardapio", []) if st == 200 else []


        selecionados = set()
        quantidades = {}

        cards_column = ft.Column(
            scroll="auto",
            expand=True,
            horizontal_alignment="center",
            alignment="center",
            spacing=15
        )

        def str_to_bool(val):
            if isinstance(val, bool):
                return val
            if isinstance(val, int):
                return val != 0
            if isinstance(val, str):
                return val.lower() in ("true", "1", "sim")
            return False

        # Depois, no loop:
        for p in itens:
            p["status"] = str_to_bool(p.get("status", True))

        # Verifica se existe pelo menos 1 produto disponível
        algum_disponivel = any(p["status"] for p in itens)

        def toggle_selecao(item, card):
            if not item["status"]:  # bloqueia clique se indisponível
                return
            if item["id"] in selecionados:
                selecionados.remove(item["id"])
                card.border = ft.border.all(1, ft.Colors.GREY)
            else:
                selecionados.add(item["id"])
                card.border = ft.border.all(3, ft.Colors.BLUE)
            page.update()

        def add_mais(item):
            if not item["status"]:
                return
            quantidades[item["id"]] = quantidades.get(item["id"], 0) + 1
            page.update()

        def add_carrinho(e):
            for item in itens:
                if not item["status"]:
                    continue
                if item["id"] in selecionados:
                    add_to_carrinho(item)
                qtd = quantidades.get(item["id"], 0)
                if qtd > 0:
                    for _ in range(qtd):
                        add_to_carrinho(item)

            selecionados.clear()
            quantidades.clear()
            page.update()
            go_carrinho()

        def comprar_agora(e):
            if not selecionados and not quantidades:
                return
            for item in itens:
                if not item["status"]:
                    continue
                if item["id"] in selecionados:
                    go_comprar(item["id"])
                qtd = quantidades.get(item["id"], 0)
                if qtd > 0:
                    for _ in range(qtd):
                        go_comprar(item["id"])
            selecionados.clear()
            quantidades.clear()
            page.update()

        # monta os cards
        for p in itens:
            if not p.get("status", True):
                continue  # 🔴 não mostra produtos inativos

            children = [
                ft.Image(src=p.get("imagem", "https://via.placeholder.com/150"), width=150, height=150),
                ft.Text(p["nome"], weight="bold"),
                ft.Text(p.get("descricao", "Sem descrição")),
                ft.Text(f"R$ {p.get('preco', 0):.2f}", color=ft.Colors.GREEN),
                ft.IconButton(
                    icon=ft.Icons.ADD_CIRCLE,
                    icon_color="blue",
                    tooltip="Adicionar mais",
                    on_click=(lambda e, item=p: add_mais(item))
                )
            ]

            card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        children,
                        alignment="center",
                        horizontal_alignment="center",
                        spacing=5
                    ),
                    padding=10,
                    border=ft.border.all(1, ft.Colors.GREY),
                    border_radius=10,
                    ink=True,
                    on_click=(lambda e, item=p: toggle_selecao(item, e.control))
                ),
                width=250
            )
            cards_column.controls.append(card)

        return ft.View(
            "/cardapio",
            controls=[
                ft.Row([cards_column], alignment="center", expand=True),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Adicionar",
                            icon=ft.Icons.SHOPPING_CART,
                            on_click=add_carrinho,
                            expand=True,
                            disabled=not algum_disponivel
                        ),

                    ],
                    spacing=10,
                    alignment="center"
                )
            ],
            vertical_alignment="center"
        )

    def add_to_carrinho(item: dict) -> None:
        """Adiciona um item ao carrinho da sessão, somando a quantidade se já existir."""
        carrinho = page.session.get("carrinho") or []

        # procura se já existe no carrinho
        for c in carrinho:
            if c["id"] == item["id"]:
                c["quantidade"] += 1
                break
        else:
            # adiciona novo
            carrinho.append({
                "id": item["id"],
                "nome": item.get("nome", "Sem nome"),
                "preco": float(item.get("preco", 0.0)),
                "quantidade": 1
            })

        page.session.set("carrinho", carrinho)
        page.update()

    def carrinho_view():
        """Renderiza a view do carrinho com atualização instantânea de + e -."""
        carrinho = page.session.get("carrinho") or []

        def salvar_carrinho():
            page.session.set("carrinho", carrinho)

        def comprar_tudo(e):
            for item in carrinho:
                api_request("POST", "/cadastrar/pedido/logado", {
                    "produto_id": item["id"],
                    "quantidade": item["quantidade"]
                })
            page.session.set("carrinho", [])
            page.update()
            go_pedidos()

        def calcular_total() -> float:
            return sum(item["preco"] * item["quantidade"] for item in carrinho)

        # Label do total para ser atualizado dinamicamente
        total_label = ft.Text(f"Total: R$ {calcular_total():.2f}", weight="bold", size=18)

        lista_itens = []
        for i in carrinho:
            # Criamos um Text separado para quantidade
            qtd_label = ft.Text(str(i["quantidade"]), size=16, weight="bold")
            subtotal_label = ft.Text(f"Subtotal: R$ {i['preco'] * i['quantidade']:.2f}", weight="w500")

            def alterar_quantidade(e, item=i, qtd_label=qtd_label, subtotal_label=subtotal_label):
                item["quantidade"] += e.control.data  # data = +1 ou -1
                if item["quantidade"] <= 0:
                    carrinho.remove(item)
                    salvar_carrinho()
                    page.go("/carrinho")  # força refresh se remover item
                    return

                qtd_label.value = str(item["quantidade"])
                subtotal_label.value = f"Subtotal: R$ {item['preco'] * item['quantidade']:.2f}"
                total_label.value = f"Total: R$ {calcular_total():.2f}"
                salvar_carrinho()

                qtd_label.update()
                subtotal_label.update()
                total_label.update()

            card = ft.Card(
                content=ft.Container(
                    padding=10,
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(i["nome"], weight="bold", size=16),
                                    ft.Text(f"Preço unitário: R$ {i['preco']:.2f}"),
                                    subtotal_label
                                ],
                                spacing=2
                            ),
                            ft.Row(
                                [
                                    ft.IconButton(
                                        ft.Icons.REMOVE,
                                        data=-1,
                                        on_click=alterar_quantidade,
                                        icon_color="red"
                                    ),
                                    qtd_label,
                                    ft.IconButton(
                                        ft.Icons.ADD,
                                        data=+1,
                                        on_click=alterar_quantidade,
                                        icon_color="green"
                                    )
                                ],
                                alignment="center"
                            )
                        ],
                        alignment="spaceBetween"
                    )
                )
            )
            lista_itens.append(card)

        return ft.View(
            "/carrinho",
            controls=[
                ft.Column(lista_itens, spacing=10) if lista_itens else ft.Text("Carrinho vazio."),
                total_label if carrinho else ft.Text(""),
                ft.ElevatedButton(
                    "Comprar Tudo",
                    on_click=lambda e: go_comprar("carrinho")
                ) if carrinho else ft.Text(""),

                ft.TextButton("Voltar", on_click=lambda _: go_cardapio())
            ]
        )

    def pedidos_view():
        st, res = api_request("GET", "/pedidos/logado")
        pedidos = res.get("pedidos", []) if st == 200 else []

        # Agrupar pedidos pela mesma data/hora
        grupos = {}
        for p in pedidos:
            chave = p.get("data")  # vem do backend
            if chave not in grupos:
                grupos[chave] = []
            grupos[chave].append(p)

        def formatar_data(data_str):
            try:
                dt = datetime.fromisoformat(data_str)
                return dt.strftime("%d/%m/%Y %H:%M")
            except:
                return "Data inválida"

        def status_color(status: str):
            if not status:
                return ft.Colors.GREY
            status = status.lower()
            if "entregue" in status:
                return ft.Colors.GREEN
            elif "cancelado" in status:
                return ft.Colors.RED
            else:
                return ft.Colors.AMBER

        cards = []
        for data, itens in grupos.items():
            produtos_column = ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(item.get("produto", "Produto"), weight="bold", expand=True),
                            ft.Text(f"x{item.get('quantidade', 1)}"),
                            ft.Text(
                                item.get("status", ""),
                                color=status_color(item.get("status", "")),
                                italic=True,
                            ),
                        ],
                        alignment="spaceBetween",
                    )
                    for item in itens
                ],
                spacing=6,
            )

            # soma do valor total dos itens do grupo
            total = sum(item.get("valor_total", 0) for item in itens)

            cards.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(f"Pedido em: {formatar_data(data)}", weight="bold", size=16),
                                produtos_column,
                                ft.Text(f"Total: R$ {total:.2f}", weight="bold", color=ft.Colors.BLUE),
                            ],
                            spacing=10,
                        ),
                        padding=12,
                        border_radius=10,
                    ),
                    elevation=2,
                )
            )

        return ft.View(
            "/pedidos",
            controls=[
                ft.Column(
                    controls=cards if cards else [ft.Text("Nenhum pedido realizado.")],
                    spacing=15,
                    scroll="auto",
                    expand=True,  # 🔥 faz ocupar espaço disponível e permitir scroll
                ),
                ft.TextButton("Voltar", on_click=lambda _: go_menu())
            ]
        )

    def editar_usuario_view():
        user = page.session.get("user") or {}
        nome = ft.TextField(label="Nome", value=user.get("nome", ""))
        telefone = ft.TextField(label="Telefone", value=user.get("telefone", ""))
        email = ft.TextField(label="Email", value=user.get("email", ""))
        senha = ft.TextField(label="Senha", password=True, can_reveal_password=True)

        def salvar(e):
            payload = {"nome": nome.value, "telefone": telefone.value, "email": email.value}
            if senha.value.strip():
                payload["senha"] = senha.value.strip()
            st, res = api_request("PUT", "/editar/usuario/logado", payload)
            if st == 200:
                page.session.set("user", res.get("usuario", payload))
            page.update()

        return ft.View(
            "/editar_usuario",
            controls=[
                nome, telefone, email, senha,
                ft.ElevatedButton("Salvar", on_click=salvar),
                ft.TextButton("Voltar", on_click=lambda _: go_menu())
            ]
        )

    def comprar_view(item_id):
        """Tela de compra (único produto ou carrinho inteiro)."""
        user_carrinho = page.session.get("carrinho") or []

        # Caso seja um item único, simulamos um "mini carrinho" com ele
        if isinstance(item_id, int):
            st, res = api_request("GET", f"/cardapio")
            produto = next((p for p in res.get("cardapio", []) if p["id"] == item_id), None)
            if not produto:
                return ft.View("/comprar", [ft.Text("Produto não encontrado.")])

            carrinho_local = [{
                "id": produto["id"],
                "nome": produto.get("nome", "Sem nome"),
                "preco": float(produto.get("preco", 0.0)),
                "quantidade": 1
            }]
        else:
            # se for "carrinho"
            carrinho_local = [dict(i) for i in user_carrinho]

        # função para salvar no session
        def salvar_carrinho():
            page.session.set("carrinho", carrinho_local)
            page.update()

        # calcular total
        def calcular_total():
            return sum(i["preco"] * i["quantidade"] for i in carrinho_local)

        # Label do total
        total_label = ft.Text(f"Total: R$ {calcular_total():.2f}", size=18, weight="bold")

        # lista dinâmica de cards
        lista_itens = ft.Column(spacing=10)

        def render_lista():
            lista_itens.controls.clear()
            for i in carrinho_local:
                qtd_label = ft.Text(str(i["quantidade"]), size=16, weight="bold")
                subtotal_label = ft.Text(f"Subtotal: R$ {i['preco'] * i['quantidade']:.2f}")

                def alterar_quantidade(e, item=i, qtd_label=qtd_label, subtotal_label=subtotal_label):
                    item["quantidade"] += e.control.data  # data = +1 ou -1
                    if item["quantidade"] <= 0:
                        carrinho_local.remove(item)
                    qtd_label.value = str(item["quantidade"])
                    subtotal_label.value = f"Subtotal: R$ {item['preco'] * item['quantidade']:.2f}"
                    total_label.value = f"Total: R$ {calcular_total():.2f}"
                    salvar_carrinho()
                    render_lista()
                    lista_itens.update()
                    total_label.update()

                card = ft.Card(
                    content=ft.Container(
                        padding=10,
                        content=ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(i["nome"], weight="bold", size=16),
                                        ft.Text(f"Preço unitário: R$ {i['preco']:.2f}"),
                                        subtotal_label
                                    ],
                                    spacing=2
                                ),
                                ft.Row(
                                    [
                                        ft.IconButton(ft.Icons.REMOVE, data=-1, on_click=alterar_quantidade,
                                                      icon_color="red"),
                                        qtd_label,
                                        ft.IconButton(ft.Icons.ADD, data=+1, on_click=alterar_quantidade,
                                                      icon_color="green")
                                    ],
                                    alignment="center"
                                )
                            ],
                            alignment="spaceBetween"
                        )
                    )
                )
                lista_itens.controls.append(card)

        render_lista()

        # ================================
        # PAGAMENTO
        # ================================
        pagamento_escolhido = {"metodo": None, "tipo_cartao": None}

        opcoes_pagamento_row = ft.Row(spacing=10, alignment="center")
        cartao_tipos_container = ft.Row(spacing=10, alignment="center", visible=False)

        def card_opcao(texto, cor, selecionado, on_click, icon_name):
            return ft.Container(
                bgcolor=cor if selecionado else "#f1f1f1",
                border_radius=10,
                padding=15,
                alignment=ft.alignment.center,
                expand=1,  # ✅ ocupa espaço proporcional no Row
                on_click=on_click,
                content=ft.Row(
                    [
                        ft.Icon(icon_name, color="white" if selecionado else "black"),
                        ft.Text(texto, size=16, weight="bold", color="white" if selecionado else "black"),
                    ],
                    alignment="center",
                    spacing=8
                ),
            )

        def render_pagamento():
            opcoes_pagamento_row.controls.clear()

            if pagamento_escolhido["metodo"] is None:
                opcoes_pagamento_row.controls.append(
                    card_opcao("Cartão", "purple", False, lambda e: escolher_pagamento("cartao"), ft.Icons.CREDIT_CARD)
                )
                opcoes_pagamento_row.controls.append(
                    card_opcao("Pix", "green", False, lambda e: escolher_pagamento("pix"), ft.Icons.PAID)
                )

            elif pagamento_escolhido["metodo"] == "cartao":
                opcoes_pagamento_row.controls.append(
                    card_opcao("Cartão", "purple", True, lambda e: escolher_pagamento(None), ft.Icons.CREDIT_CARD)
                )
                cartao_tipos_container.visible = True

            elif pagamento_escolhido["metodo"] == "pix":
                opcoes_pagamento_row.controls.append(
                    card_opcao("Pix", "green", True, lambda e: escolher_pagamento(None), ft.Icons.PAID)
                )
                cartao_tipos_container.visible = False

            # só atualiza se já estiver na página
            if opcoes_pagamento_row.page:
                opcoes_pagamento_row.update()
            if cartao_tipos_container.page:
                cartao_tipos_container.update()

        def escolher_pagamento(metodo):
            if pagamento_escolhido["metodo"] == metodo:
                pagamento_escolhido["metodo"] = None
                pagamento_escolhido["tipo_cartao"] = None
            else:
                pagamento_escolhido["metodo"] = metodo
                pagamento_escolhido["tipo_cartao"] = None

            render_pagamento()
            render_cartao_tipos()

        def escolher_tipo_cartao(tipo):
            pagamento_escolhido["tipo_cartao"] = tipo
            render_cartao_tipos()

        def render_cartao_tipos():
            cartao_tipos_container.controls.clear()
            if pagamento_escolhido["metodo"] == "cartao":
                cartao_tipos_container.controls.append(
                    card_opcao("Débito", "purple", pagamento_escolhido["tipo_cartao"] == "debito",
                               lambda e: escolher_tipo_cartao("debito"), ft.Icons.ATM)
                )
                cartao_tipos_container.controls.append(
                    card_opcao("Crédito", "purple", pagamento_escolhido["tipo_cartao"] == "credito",
                               lambda e: escolher_tipo_cartao("credito"), ft.Icons.CREDIT_CARD)
                )
            if cartao_tipos_container.page:
                cartao_tipos_container.update()

            if cartao_tipos_container.page:
                cartao_tipos_container.update()

        # ================================
        # CONFIRMAR COMPRA
        # ================================
        def confirmar(e):
            if not pagamento_escolhido["metodo"]:
                page.snack_bar = ft.SnackBar(ft.Text("Selecione um método de pagamento!"), bgcolor="red")
                page.snack_bar.open = True
                page.update()
                return

            if pagamento_escolhido["metodo"] == "cartao" and not pagamento_escolhido["tipo_cartao"]:
                page.snack_bar = ft.SnackBar(ft.Text("Selecione débito ou crédito!"), bgcolor="red")
                page.snack_bar.open = True
                page.update()
                return

            metodo_final = (
                pagamento_escolhido["metodo"]
                if pagamento_escolhido["metodo"] != "cartao"
                else pagamento_escolhido["tipo_cartao"]
            )

            for item in carrinho_local:
                payload = {
                    "produto_id": item["id"],
                    "quantidade": item["quantidade"],
                    "metodo_pagamento": metodo_final
                }
                api_request("POST", "/cadastrar/pedido/logado", payload)

            page.session.set("carrinho", [])
            go_pedidos()

        # ================================
        # RETORNO DA TELA
        # ================================
        view = ft.View(
            f"/comprar/{item_id}",
            controls=[
                ft.Text("Resumo da Compra", size=20, weight="bold"),
                lista_itens,
                total_label,
                ft.Divider(),
                ft.Text("Escolha o método de pagamento:", size=16, weight="w500"),
                opcoes_pagamento_row,
                cartao_tipos_container,
                ft.Divider(),
                ft.ElevatedButton("Confirmar Compra", on_click=confirmar),
                ft.TextButton("Voltar", on_click=lambda _: go_carrinho())
            ],
            scroll="auto"
        )

        # agora sim renderiza depois que o view foi criado
        render_pagamento()
        render_cartao_tipos()

        return view

    def do_logout():
        page.session.set("token", None)
        page.session.set("user", None)
        page.update()
        go_login()

    def go_login(): page.go("/login")
    def go_cadastro(): page.go("/cadastro")
    def go_menu(): page.go("/menu")
    def go_cardapio(): page.go("/cardapio")
    def go_carrinho(): page.go("/carrinho")
    def go_pedidos(): page.go("/pedidos")
    def go_editar_usuario(): page.go("/editar_usuario")
    def go_comprar(pid): page.go(f"/comprar/{pid}")

    def route_change(route):
        # por padrão, esconde o FAB
        page.floating_action_button = None

        if page.route == "/login":
            page.views.clear(); page.views.append(login_view())
        elif page.route == "/cadastro":
            page.views.clear(); page.views.append(cadastro_view())
        elif page.route == "/menu":
            page.views.clear(); page.views.append(menu_view())
        elif page.route == "/cardapio":
            page.views.clear(); page.views.append(cardapio_view())
        elif page.route == "/carrinho":
            page.views.clear(); page.views.append(carrinho_view())
        elif page.route == "/pedidos":
            page.views.clear(); page.views.append(pedidos_view())
        elif page.route == "/editar_usuario":
            page.views.clear(); page.views.append(editar_usuario_view())
        elif page.route.startswith("/comprar/"):
            pid = page.route.split("/")[-1]
            item_id = int(pid) if pid.isdigit() else pid  # aceita "carrinho" também
            page.views.clear()
            page.views.append(comprar_view(item_id))

        page.update()

    page.on_route_change = route_change
    page.go("/login")


ft.app(target=main)
