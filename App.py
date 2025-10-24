import flet as ft
import requests
from datetime import datetime, timezone
import pytz
import asyncio

BASE_URL = "http://192.168.1.83:5002"

pedido_global_counter = 0
BR_TZ = pytz.timezone("America/Sao_Paulo")



def main(page: ft.Page):
    page.title = "SmartSell"
    page.session.set("token", None)
    page.session.set("user", None)
    page.theme_mode = "light"
    page.window.height = 900
    page.window.width = 440


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

    def login_view(page, go_cardapio, go_cadastro, api_request):
        # === Cores principais ===
        PRIMARY = "#FFD54F"  # amarelo claro
        ACCENT = "#FF9800"  # laranja
        TEXT = "#212121"  # preto suave
        BG = "#FFFFFF"  # branco
        GREY = "#E0E0E0"  # cinza leve
        ERROR = "#E53935"  # vermelho para erros
        INPUT_BG = "#FAFAFA"

        # === Campos de login ===
        email = ft.TextField(
            label="Email",
            border_color=GREY,
            color=TEXT,
            border_radius=12,
            width=300,
            bgcolor=INPUT_BG,
            focused_border_color=PRIMARY,
            label_style=ft.TextStyle(color="#757575")
        )
        senha = ft.TextField(
            label="Senha",
            password=True,
            can_reveal_password=True,
            border_color=GREY,
            color=TEXT,
            border_radius=12,
            width=300,
            bgcolor=INPUT_BG,
            focused_border_color=PRIMARY,
            label_style=ft.TextStyle(color="#757575")
        )

        mensagem = ft.Text("", color=ERROR, size=12)

        # === Função de login ===
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
                go_cardapio()
            else:
                mensagem.value = "Email ou senha incorretos."
                page.update()

        # === Botão estilizado com hover ===
        login_button = ft.ElevatedButton(
            "Entrar",
            on_click=do_login,
            style=ft.ButtonStyle(
                bgcolor=PRIMARY,
                color=TEXT,
                overlay_color=ACCENT,
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.Padding(16, 0, 16, 0),
                text_style=ft.TextStyle(weight="bold"),
            ),
            width=300,
        )

        # === Cartão de Login com gradiente sutil e sombra ===
        card_login = ft.Container(
            width=360,
            padding=40,
            border_radius=24,
            bgcolor=BG,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[BG, "#FFF8E1"]
            ),
            shadow=ft.BoxShadow(
                color="#00000020",
                blur_radius=30,
                offset=ft.Offset(0, 10)
            ),
            content=ft.Column(
                [
                    ft.Text("Bem-vindo 👋", size=24, weight="bold", color=TEXT),
                    ft.Text("Entre com sua conta para continuar", size=14, color="#757575"),
                    ft.Divider(height=20, color="transparent"),

                    email,
                    senha,
                    mensagem,
                    login_button,
                    ft.TextButton(
                        "Cadastrar-se",
                        on_click=lambda _: go_cadastro(),
                        style=ft.ButtonStyle(
                            color=ACCENT,
                            overlay_color="#FFE0B2"
                        ),
                    ),
                ],
                alignment="center",
                horizontal_alignment="center",
                spacing=14
            )
        )

        # === Layout central ===
        return ft.View(
            "/login",
            bgcolor=BG,
            horizontal_alignment="center",
            vertical_alignment="center",
            controls=[
                ft.Column(
                    [
                        card_login,
                        ft.Text("© 2025 SanctusPanis", size=11, color="#9E9E9E"),
                    ],
                    alignment="center",
                    horizontal_alignment="center",
                    spacing=20
                )
            ]
        )

    def cadastro_view(page, go_login, api_request):
        # === Cores principais ===
        PRIMARY = "#FFD54F"  # amarelo claro
        ACCENT = "#FF9800"  # laranja
        TEXT = "#212121"  # preto suave
        BG = "#FFFFFF"  # branco
        GREY = "#E0E0E0"  # cinza leve
        ERROR = "#E53935"  # vermelho
        INPUT_BG = "#FAFAFA"

        # === Campos de cadastro ===
        nome = ft.TextField(
            label="Nome",
            border_color=GREY,
            color=TEXT,
            border_radius=12,
            width=300,
            bgcolor=INPUT_BG,
            focused_border_color=PRIMARY,
            label_style=ft.TextStyle(color="#757575")
        )
        email = ft.TextField(
            label="Email",
            border_color=GREY,
            color=TEXT,
            border_radius=12,
            width=300,
            bgcolor=INPUT_BG,
            focused_border_color=PRIMARY,
            label_style=ft.TextStyle(color="#757575")
        )
        telefone = ft.TextField(
            label="Telefone",
            border_color=GREY,
            color=TEXT,
            border_radius=12,
            width=300,
            bgcolor=INPUT_BG,
            focused_border_color=PRIMARY,
            label_style=ft.TextStyle(color="#757575")
        )
        senha = ft.TextField(
            label="Senha",
            password=True,
            can_reveal_password=True,
            border_color=GREY,
            color=TEXT,
            border_radius=12,
            width=300,
            bgcolor=INPUT_BG,
            focused_border_color=PRIMARY,
            label_style=ft.TextStyle(color="#757575")
        )

        mensagem = ft.Text("", color=ERROR, size=12)

        # === Função de cadastro ===
        def do_cadastro(e):
            try:
                status, res = api_request("POST", "/usuario/cadastro", {
                    "nome": nome.value,
                    "telefone": telefone.value,
                    "email": email.value,
                    "senha": senha.value
                })
                print("🔍 Resposta da API:", status, res)

                if status == 201:
                    go_login()
                else:
                    mensagem.value = f"Erro no cadastro: {res}"
                    page.update()

            except Exception as err:
                print("❌ Erro inesperado no cadastro:", err)
                mensagem.value = f"Erro interno: {err}"
                page.update()

        # === Botão estilizado ===
        cadastro_button = ft.ElevatedButton(
            "Criar Conta",
            on_click=do_cadastro,
            style=ft.ButtonStyle(
                bgcolor=PRIMARY,
                color=TEXT,
                overlay_color=ACCENT,
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.Padding(16, 0, 16, 0),
                text_style=ft.TextStyle(weight="bold"),
            ),
            width=300,
        )

        # === Card de Cadastro ===
        card_cadastro = ft.Container(
            width=380,
            padding=40,
            border_radius=24,
            bgcolor=BG,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[BG, "#FFF8E1"]
            ),
            shadow=ft.BoxShadow(
                color="#00000020",
                blur_radius=30,
                offset=ft.Offset(0, 10)
            ),
            content=ft.Column(
                [
                    ft.Text("Criar Conta 📝", size=24, weight="bold", color=TEXT),
                    ft.Text("Preencha os dados abaixo para se cadastrar", size=14, color="#757575"),
                    ft.Divider(height=20, color="transparent"),

                    nome,
                    email,
                    telefone,
                    senha,
                    mensagem,
                    cadastro_button,
                    ft.TextButton(
                        "Já tem conta? Entrar",
                        on_click=lambda _: go_login(),
                        style=ft.ButtonStyle(
                            color=ACCENT,
                            overlay_color="#FFE0B2"
                        ),
                    ),
                ],
                alignment="center",
                horizontal_alignment="center",
                spacing=14
            )
        )

        # === Layout central ===
        return ft.View(
            "/cadastro",
            bgcolor=BG,
            horizontal_alignment="center",
            vertical_alignment="center",
            controls=[
                ft.Column(
                    [
                        card_cadastro,
                        ft.Text("© 2025 SanctusPanis", size=11, color="#9E9E9E"),
                    ],
                    alignment="center",
                    horizontal_alignment="center",
                    spacing=20
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
        st, res = api_request("GET", "/cardapio/listar")
        itens = res.get("cardapio", []) if st == 200 else []

        selecionados = set()
        quantidades = {}
        current_cat = "TODOS"

        # Normalização de status e categoria
        def str_to_bool(val):
            if isinstance(val, bool):
                return val
            if isinstance(val, int):
                return val != 0
            if isinstance(val, str):
                return val.lower() in ("true", "1", "sim")
            return False

        for p in itens:
            p["status"] = str_to_bool(p.get("status", True))
            categoria = (p.get("categoria") or "").strip()
            p["categoria"] = categoria if categoria else "OUTROS"

        algum_disponivel = any(p["status"] for p in itens)

        # Categorias dinâmicas (com TODOS sempre no início)
        categorias_set = sorted({
            p.get("categoria", "").upper() for p in itens if p.get("categoria") is not None
        })
        categorias = ["TODOS"] + [c for c in categorias_set if c != "TODOS"]

        # Grid principal
        grid = ft.Column(
            scroll="auto",
            expand=True,
            alignment="center",
            horizontal_alignment="center",
            spacing=15,
        )

        # ===== Funções auxiliares =====

        def toggle_selecao(item, control):
            if not item["status"]:
                return
            if item["id"] in selecionados:
                selecionados.remove(item["id"])
                control.border = ft.border.all(1, ft.Colors.GREY)
            else:
                selecionados.add(item["id"])
                control.border = ft.border.all(3, ft.Colors.BLUE)
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
                for _ in range(quantidades.get(item["id"], 0)):
                    add_to_carrinho(item)
            selecionados.clear()
            quantidades.clear()
            page.update()
            go_carrinho()

        # Campo de busca
        search_field = ft.TextField(
            hint_text="Pesquisar...",
            prefix_icon=ft.Icons.SEARCH,
            border_color="grey",
            bgcolor="white",
            width=240,
            height=45,
        )

        # ===== Função de exibição principal =====
        def mostrar_categoria(cat):
            nonlocal current_cat
            current_cat = cat
            grid.controls.clear()

            query = (search_field.value or "").strip().lower()

            def criar_card(produto):
                """Gera um card de produto visualmente consistente."""
                return ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Container(
                                    bgcolor="#FFB84D",
                                    height=70,
                                    width=150,
                                    border_radius=ft.border_radius.only(top_left=10, top_right=10),
                                ),
                                ft.Text(produto["nome"], weight="bold"),
                                ft.Text(f"R$ {produto.get('preco', 0):.2f}", color=ft.Colors.GREEN),
                                ft.IconButton(
                                    icon=ft.Icons.ADD_CIRCLE,
                                    icon_color="orange",
                                    on_click=lambda e, item=produto: add_mais(item),
                                ),
                            ],
                            alignment="center",
                            horizontal_alignment="center",
                            spacing=5,
                        ),
                        padding=10,
                        border=ft.border.all(1, ft.Colors.GREY),
                        border_radius=10,
                        ink=True,
                        on_click=lambda e, item=produto: toggle_selecao(item, e.control),
                    ),
                    width=150,
                    height=180,
                )

            def render_linha(produtos):
                linha = []
                for p in produtos:
                    linha.append(criar_card(p))
                    if len(linha) == 2:
                        grid.controls.append(ft.Row(linha, alignment="center", spacing=15))
                        linha = []
                if linha:
                    grid.controls.append(ft.Row(linha, alignment="center", spacing=15))

            # Busca
            if query:
                encontrados = [p for p in itens if p.get("status", True) and query in p.get("nome", "").lower()]
                if not encontrados:
                    grid.controls.append(ft.Text("Nenhum produto encontrado.", size=16))
                else:
                    render_linha(encontrados)

            else:
                # Agrupamento e ordenação de categorias
                if cat == "TODOS":
                    def category_sort_key(c):
                        c = c.upper()
                        if "LANC" in c: return (0, c)
                        if "DOCE" in c: return (1, c)
                        if "BEB" in c:  return (2, c)
                        return (3, c)

                    categorias_presentes = sorted(
                        {p["categoria"].upper() for p in itens if p.get("status", True)},
                        key=category_sort_key
                    )

                    for categoria in categorias_presentes:
                        produtos_cat = [p for p in itens if p["status"] and p["categoria"].upper() == categoria]
                        if not produtos_cat:
                            continue
                        grid.controls.append(ft.Text(categoria, size=18, weight="bold"))
                        render_linha(produtos_cat)

                else:
                    produtos = [p for p in itens if p.get("status", True) and p.get("categoria", "").upper() == cat]
                    if not produtos:
                        grid.controls.append(ft.Text("Nenhum produto nesta categoria.", size=16))
                    else:
                        render_linha(produtos)

            page.update()

        # ===== Eventos =====
        search_field.on_change = mostrar_categoria
        search_field.on_submit = mostrar_categoria

        # Topo com busca + ícones
        topo = ft.Container(
            content=ft.Row(
                [
                    search_field,
                    ft.IconButton(icon=ft.Icons.ACCOUNT_CIRCLE, icon_size=30, on_click=lambda _: go_editar_usuario()),

                ],
                alignment="spaceBetween",
                vertical_alignment="center",
                spacing=10,
            ),
            border=ft.border.only(bottom=ft.BorderSide(1, "grey")),
            padding=10,
        )

        # Botões de categoria
        cat_buttons = [
            ft.ElevatedButton(
                c,
                bgcolor="#FFD54F",
                color="black",
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=20),
                    padding=15,
                ),
                on_click=lambda e, cat=c: mostrar_categoria(cat),
            )
            for c in categorias
        ]

        # Render inicial
        mostrar_categoria("TODOS")

        return ft.View(
            "/cardapio",
            controls=[
                topo,
                ft.Row(cat_buttons, alignment="center", spacing=10),
                grid,
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "ADICIONAR",
                            icon=ft.Icons.SHOPPING_CART,
                            bgcolor="#FFD54F",
                            color="black",
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=25),
                                padding=20,
                            ),
                            on_click=add_carrinho,
                            expand=True,
                            disabled=not algum_disponivel,
                        ),
                    ],
                    spacing=10,
                    alignment="center",

                ),

            ],
            vertical_alignment="start",
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

        total_label = ft.Text(
            f"Total: R$ {calcular_total():.2f}",
            weight="bold",
            size=22,
            color=ft.Colors.AMBER_800
        )

        lista_itens = []
        for i in carrinho:
            qtd_label = ft.Text(str(i["quantidade"]), size=16, weight="bold")
            subtotal_label = ft.Text(
                f"Subtotal: R$ {i['preco'] * i['quantidade']:.2f}",
                weight="w600",
                color=ft.Colors.GREY_600
            )

            def alterar_quantidade(e, item=i, qtd_label=qtd_label, subtotal_label=subtotal_label):
                item["quantidade"] += e.control.data
                if item["quantidade"] <= 0:
                    carrinho.remove(item)
                    salvar_carrinho()
                    page.go("/carrinho")
                    return

                qtd_label.value = str(item["quantidade"])
                subtotal_label.value = f"Subtotal: R$ {item['preco'] * item['quantidade']:.2f}"
                total_label.value = f"Total: R$ {calcular_total():.2f}"
                salvar_carrinho()

                qtd_label.update()
                subtotal_label.update()
                total_label.update()

            card = ft.Container(
                bgcolor=ft.Colors.WHITE,
                border_radius=15,
                shadow=ft.BoxShadow(
                    blur_radius=12,
                    color=ft.Colors.GREY_500,  # sombra mais natural e escura
                    spread_radius=0.4,
                    offset=ft.Offset(0, 3),
                ),
                padding=15,
                margin=ft.margin.only(bottom=10),
                content=ft.Row(
                    [
                        ft.Container(
                            width=55,
                            height=55,
                            bgcolor=ft.Colors.AMBER_100,
                            border_radius=10,
                            alignment=ft.alignment.center,
                            content=ft.Icon(ft.Icons.SHOPPING_BASKET, color=ft.Colors.AMBER_700, size=28)
                        ),
                        ft.Column(
                            [
                                ft.Text(i["nome"], weight="bold", size=17, color=ft.Colors.BLACK),
                                ft.Text(f"Preço: R$ {i['preco']:.2f}", color=ft.Colors.GREY_700, size=13),
                                subtotal_label
                            ],
                            spacing=3,
                            expand=True
                        ),
                        ft.Row(
                            [
                                ft.IconButton(
                                    ft.Icons.REMOVE_CIRCLE_OUTLINE,
                                    data=-1,
                                    on_click=alterar_quantidade,
                                    icon_color=ft.Colors.RED_600,
                                ),
                                qtd_label,
                                ft.IconButton(
                                    ft.Icons.ADD_CIRCLE_OUTLINE,
                                    data=+1,
                                    on_click=alterar_quantidade,
                                    icon_color=ft.Colors.GREEN_600,
                                )
                            ],
                            alignment="center"
                        )
                    ],
                    alignment="spaceBetween"
                )
            )
            lista_itens.append(card)

        # === Área de scroll ===
        scroll_area = ft.Container(
            expand=True,
            content=ft.Column(
                lista_itens,
                spacing=10,
                scroll=ft.ScrollMode.AUTO
            ) if lista_itens else ft.Container(
                content=ft.Text("Carrinho vazio 😴", size=18, color=ft.Colors.GREY_600, italic=True),
                alignment=ft.alignment.center,
                padding=50,
            )
        )

        # === Rodapé fixo (sem card, limpo e centralizado) ===
        bottom_bar = ft.Container(
            content=ft.Column(
                [
                    total_label if carrinho else ft.Text(""),

                    ft.Row(
                        [
                            ft.TextButton(
                                "⬅ Voltar",
                                on_click=lambda _: go_cardapio(),
                                expand=True,  # ocupa metade do espaço
                                style=ft.ButtonStyle(
                                    color=ft.Colors.AMBER_800,
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                    padding=ft.padding.symmetric(vertical=14),
                                    side=ft.BorderSide(1, ft.Colors.AMBER_700),
                                )
                            ),
                            ft.ElevatedButton(
                                "Finalizar Compra",
                                on_click=lambda e: go_comprar("carrinho"),
                                expand=True,  # ocupa metade do espaço
                                bgcolor=ft.Colors.AMBER_700,
                                color=ft.Colors.WHITE,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                    padding=ft.padding.symmetric(vertical=14),
                                    elevation=3,
                                )
                            ),
                        ],
                        alignment="center",
                        spacing=15
                    )
                ],
                spacing=15,
                horizontal_alignment="center",
            ),
            padding=ft.padding.only(top=10, bottom=20, left=10, right=10),
        )

        return ft.View(
            "/carrinho",
            controls=[
                ft.AppBar(
                    title=ft.Text("🛒 Meu Carrinho", size=22, weight="bold"),
                    bgcolor=ft.Colors.AMBER_700,
                    color=ft.Colors.WHITE,
                    center_title=True,
                ),
                ft.Container(
                    bgcolor=ft.Colors.AMBER_50,
                    expand=True,
                    content=ft.Column(
                        [
                            scroll_area,
                            bottom_bar
                        ],
                        expand=True,
                        alignment="spaceBetween"
                    ),
                    padding=20
                )
            ]
        )

    def pedidos_view():
        st, res = api_request("GET", "/pedidos/logado")
        pedidos = res.get("pedidos", []) if st == 200 else []

        last_route = page.session.get("last_route") or "/perfil_view"

        def formatar_data_display(data_str):
            """Retorna a data formatada bonitinha para exibir no card."""
            try:
                dt = datetime.fromisoformat(data_str.replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                dt_br = dt.astimezone(BR_TZ)
                return dt_br.strftime("%d/%m/%Y %H:%M:%S")
            except:
                return "Data inválida"

        def normalizar_data(data_str):
            """Retorna a data normalizada (chave exata)."""
            try:
                return datetime.fromisoformat(data_str.replace("Z", "+00:00")).isoformat()
            except:
                return data_str  # fallback caso erro

        # Agrupar pedidos pelo mesmo datetime completo
        pedidos_dict = {}
        for p in pedidos:
            data_key = normalizar_data(p.get("data", ""))
            if data_key not in pedidos_dict:
                pedidos_dict[data_key] = {
                    "itens": [],
                    "status": p.get("status", "Pendente"),
                    "data": p.get("data", ""),
                    "valor_total": 0.0,
                }
            pedidos_dict[data_key]["itens"].append(p)
            pedidos_dict[data_key]["valor_total"] += p.get("valor_total", 0.0)

        cards = []
        for data_key, pedido in pedidos_dict.items():
            status = pedido["status"]
            valor_total = pedido["valor_total"]
            data_display = formatar_data_display(pedido["data"])

            # Definir ícone do status
            if "entregue" in status.lower():
                status_icon = ft.Icon(name=ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=26)
            elif "cancelado" in status.lower():
                status_icon = ft.Icon(name=ft.Icons.CANCEL, color=ft.Colors.RED, size=26)
            else:
                status_icon = ft.Icon(name=ft.Icons.HOURGLASS_BOTTOM, color=ft.Colors.AMBER, size=26)

            # Lista de itens do pedido (mesmo horário exato)
            itens_col = []
            for item in pedido["itens"]:
                itens_col.append(
                    ft.Row(
                        [
                            ft.CircleAvatar(
                                foreground_image_src=item.get("imagem", "https://via.placeholder.com/50"),
                                radius=20,
                            ),
                            ft.Text(item.get("produto", "Produto"), size=13, weight="w500"),
                        ],
                        spacing=8,
                    )
                )

            # Card agrupado
            card = ft.Container(
                bgcolor=ft.Colors.WHITE,
                border_radius=15,
                padding=15,
                shadow=ft.BoxShadow(blur_radius=8, spread_radius=2, color=ft.Colors.BLACK12),
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(data_display, size=15, weight="bold"),
                                status_icon,
                            ],
                            alignment="spaceBetween",
                        ),
                        ft.Text(f"Status: {status.upper()}", size=12, italic=True, color=ft.Colors.GREY),
                        ft.Divider(),
                        ft.Column(itens_col, spacing=5),
                        ft.Divider(),
                        ft.Text(f"TOTAL: R$ {valor_total:.2f}", size=14, weight="bold", color=ft.Colors.BLACK),
                    ],
                    spacing=8,
                ),
            )
            cards.append(card)

        return ft.View(
            "/pedidos",
            controls=[
                ft.Column(
                    controls=cards if cards else [ft.Text("Nenhum pedido realizado.")],
                    spacing=15,
                    scroll="auto",
                    expand=True,
                ),
                ft.Row(
                    alignment="spaceBetween",
                    controls=[
                        ft.Container(
                            alignment=ft.alignment.center_left,
                            padding=10,
                            content=ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                icon_color=ft.Colors.BLACK,
                                bgcolor=ft.Colors.AMBER,
                                icon_size=28,
                                on_click=lambda _: page.go(last_route),
                            ),
                        ),
                        ft.Container(
                            alignment=ft.alignment.center_right,
                            padding=10,
                            content=ft.IconButton(
                                icon=ft.Icons.RESTAURANT_MENU,
                                icon_color=ft.Colors.BLACK,
                                bgcolor=ft.Colors.AMBER,
                                icon_size=28,
                                on_click=lambda _: go_cardapio(),
                            ),
                        ),
                    ],
                ),
            ],
        )

    def perfil_view(page, api_request, go_menu, go_pedidos):
        import asyncio
        user = page.session.get("user") or {}
        editing_global = {"on": False}
        dirty = {"changed": False}
        fields = {}

        # --- Helpers ---
        def atualizar_sessao_e_ui(novo_usuario):
            page.session.set("user", novo_usuario)
            page.update()

        def patch_usuario(payload):
            st, res = api_request("PUT", "/editar/usuario/logado", payload)
            return st, res

        # --- Campo com edição inline ---
        def make_field(key, label, value, password=False, placeholder=""):
            display_txt = ft.Text(value or "-", size=14, color="black")
            tf = ft.TextField(
                value=value or "",
                visible=False,
                password=password,
                can_reveal_password=(password is True),
                width=280,  # fixado, menor para não empurrar ícone
                height=40,
                border_color="#cccccc",
                bgcolor="#fffbe6",
                color="black",
                label=label,
            )

            pencil = ft.IconButton(
                icon=ft.Icons.EDIT,
                icon_color="orange",
                tooltip=f"Editar {label}",
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))
            )

            def enter_edit_mode(e):
                tf.visible = True
                display_txt.visible = False
                pencil.icon = ft.Icons.SAVE_ALT  # ícone de salvar temporário
                pencil.icon_color = "#4CAF50"
                pencil.tooltip = f"Salvar {label}"
                page.update()

            def save_field(e):
                new_val = tf.value.strip()
                display_txt.value = new_val or "-"
                tf.visible = False
                display_txt.visible = True

                # ícone de check breve
                pencil.icon = ft.Icons.CHECK_CIRCLE
                pencil.icon_color = "#4CAF50"
                pencil.tooltip = "Campo salvo!"
                page.update()

                async def revert_after_delay():
                    await asyncio.sleep(1)
                    pencil.icon = ft.Icons.EDIT
                    pencil.icon_color = "orange"
                    pencil.tooltip = f"Editar {label}"
                    page.update()

                page.run_task(revert_after_delay)
                dirty["changed"] = True

            def on_pencil_click(e):
                if tf.visible:
                    save_field(e)
                else:
                    enter_edit_mode(e)

            pencil.on_click = on_pencil_click

            container = ft.Row(
                [
                    ft.Container(
                        content=ft.Column(
                            [ft.Text(label, size=12, color="#444"), display_txt, tf],
                            spacing=2
                        ),
                        width=300
                    ),
                    pencil,
                ],
                alignment="spaceBetween",
                vertical_alignment="center",
                spacing=8,
            )
            fields[key] = {"display": display_txt, "tf": tf, "pencil": pencil, "label": label}
            return container

        # --- Campos ---
        nome_row = make_field("nome", "Nome completo", user.get("nome", ""))
        tel_row = make_field("telefone", "Telefone", user.get("telefone", ""))
        email_row = make_field("email", "E-mail", user.get("email", ""))
        senha_tf = ft.TextField(label="Nova senha", password=True, can_reveal_password=True, visible=False, width=280)

        def toggle_senha(e):
            senha_tf.visible = not senha_tf.visible
            page.update()

        trocar_senha_btn = ft.TextButton(
            "Alterar senha",
            on_click=toggle_senha,
            style=ft.ButtonStyle(color="orange"),
        )

        # --- Campo de senha ---
        senha_tf = ft.TextField(
            label="Nova senha",
            password=True,
            can_reveal_password=True,
            visible=False,
            width=320,
            height=42,
            border_color="#cccccc",
            bgcolor="#fffbe6",
            color="black",
        )

        # Ícone de salvar senha (só aparece quando campo está ativo)
        salvar_senha_icon = ft.IconButton(
            icon=ft.Icons.SAVE_ALT,
            icon_color="#4CAF50",
            tooltip="Salvar nova senha",
            visible=False,
        )

        def toggle_senha(e):
            senha_tf.visible = not senha_tf.visible
            salvar_senha_icon.visible = senha_tf.visible
            page.update()

        def salvar_senha(e):
            nova_senha = senha_tf.value.strip()
            if not nova_senha:
                page.snack_bar = ft.SnackBar(ft.Text("Digite uma nova senha!"), bgcolor="#FF9800")
                page.snack_bar.open = True
                page.update()
                return

            st, res = patch_usuario({"senha": nova_senha})
            if st == 200:
                senha_tf.value = ""
                senha_tf.visible = False
                salvar_senha_icon.visible = False
                page.snack_bar = ft.SnackBar(ft.Text("Senha atualizada com sucesso!"), bgcolor="#4CAF50")
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Falha ao atualizar senha."), bgcolor="#FF9800")

            page.snack_bar.open = True
            page.update()

        salvar_senha_icon.on_click = salvar_senha

        trocar_senha_btn = ft.TextButton(
            "Alterar senha",
            on_click=toggle_senha,
            style=ft.ButtonStyle(color="orange"),
        )

        # Container de senha, botão e ícone centralizados
        senha_container = ft.Column(
            [
                ft.Container(content=trocar_senha_btn, alignment=ft.alignment.center),
                ft.Container(content=senha_tf, alignment=ft.alignment.center),
                ft.Container(content=salvar_senha_icon, alignment=ft.alignment.center),
            ],
            horizontal_alignment="center",
            spacing=8,
        )

        # --- Modo edição global ---
        def entrar_modo_edicao_global():
            editing_global["on"] = True
            for k, ref in fields.items():
                ref["tf"].visible = True
                ref["display"].visible = False
                ref["pencil"].visible = False
            save_btn.visible = True
            cancel_btn.visible = True
            edit_btn.visible = False
            page.update()

        def cancelar_edicao(e):
            editing_global["on"] = False
            dirty["changed"] = False
            sess = page.session.get("user") or {}
            for k, ref in fields.items():
                val = sess.get(k, "")
                ref["tf"].value = val
                ref["display"].value = val or "-"
                ref["tf"].visible = False
                ref["display"].visible = True
                ref["pencil"].visible = True
            senha_tf.value = ""
            senha_tf.visible = False
            save_btn.visible = False
            cancel_btn.visible = False
            edit_btn.visible = True
            page.update()

        def salvar_tudo(e):
            payload = {}
            for k, ref in fields.items():
                payload[k] = ref["tf"].value.strip()
            if senha_tf.visible and senha_tf.value.strip():
                payload["senha"] = senha_tf.value.strip()
            try:
                st, res = patch_usuario(payload)
                if st == 200:
                    novo = res.get("usuario", payload)
                    sess = page.session.get("user") or {}
                    sess.update(novo)
                    atualizar_sessao_e_ui(sess)
                    page.snack_bar = ft.SnackBar(ft.Text("Perfil atualizado com sucesso"), bgcolor="#4CAF50")
                    page.snack_bar.open = True
                    cancelar_edicao(e)
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("Falha ao atualizar."), bgcolor="#FF9800")
                    page.snack_bar.open = True
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Erro: {ex}"), bgcolor="#FF9800")
                page.snack_bar.open = True
            page.update()

        # --- Botões ---
        edit_btn = ft.ElevatedButton("Editar perfil", icon=ft.Icons.EDIT,
                                     on_click=lambda e: entrar_modo_edicao_global(),
                                     bgcolor="orange", color="white")
        save_btn = ft.ElevatedButton("Salvar", icon=ft.Icons.CHECK, on_click=salvar_tudo, visible=False,
                                     bgcolor="#4CAF50", color="white")
        cancel_btn = ft.ElevatedButton("Cancelar", icon=ft.Icons.CANCEL, on_click=cancelar_edicao, visible=False,
                                       bgcolor="#F44336", color="white")

        pedidos_btn = ft.ElevatedButton("Meus Pedidos", icon=ft.Icons.RECEIPT_LONG,
                                        on_click=lambda e: go_pedidos(),
                                        bgcolor="orange", color="white")
        voltar_btn = ft.TextButton("Voltar", on_click=lambda e: go_menu(), style=ft.ButtonStyle(color="#555"))

        # --- Layout principal ---
        info_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Minha Conta", size=22, weight="bold", color="black"),
                        ft.Text(user.get("email", ""), size=13, color="#555"),
                        ft.Row([edit_btn, save_btn, cancel_btn], alignment="center", spacing=12),
                        ft.Divider(height=25),
                        nome_row,
                        ft.Divider(),
                        tel_row,
                        ft.Divider(),
                        email_row,
                        ft.Divider(),
                        senha_container,

                    ],
                    horizontal_alignment="center",
                    spacing=12,
                ),
                padding=20,
                width=400,
                bgcolor="white",
                border_radius=12,
                shadow=ft.BoxShadow(blur_radius=12, spread_radius=1, color=ft.Colors.with_opacity(0.2, "black")),
            ),
            elevation=0,
        )

        actions_row = ft.Row(
            [pedidos_btn],
            alignment="center",
            spacing=0,
        )

        def inicializar_campos():
            sess = page.session.get("user") or {}
            for k, ref in fields.items():
                val = sess.get(k, "")
                ref["display"].value = val or "-"
                ref["tf"].value = val or ""

        inicializar_campos()

        return ft.View(
            "/perfil",
            controls=[
                ft.Container(
                    bgcolor="#f5f5f5",
                    expand=True,
                    content=ft.Column(
                        [
                            ft.Container(
                                content=info_card,
                                alignment=ft.alignment.center,
                                padding=ft.padding.only(top=40),
                            ),
                            ft.Container(
                                content=actions_row,
                                padding=ft.padding.only(top=10, bottom=10),
                            ),

                            # botão de voltar centralizado no rodapé
                            ft.Container(
                                alignment=ft.alignment.center,
                                padding=ft.padding.only(bottom=25, top=20),
                                content=ft.IconButton(
                                    icon=ft.Icons.ARROW_BACK,
                                    icon_color=ft.Colors.BLACK,
                                    bgcolor="orange",
                                    icon_size=32,
                                    on_click=lambda _: go_cardapio(),
                                ),
                            ),
                        ],
                        horizontal_alignment="center",
                        spacing=16,
                        alignment="spaceBetween",  # garante espaçamento entre topo e base
                    ),
                )
            ],
            vertical_alignment="center",
            horizontal_alignment="center",
        )
    def comprar_view(item_id):
        """Tela de compra (único produto ou carrinho inteiro)."""
        user_carrinho = page.session.get("carrinho") or []

        # 🔹 Se veio um ID, simula um carrinho com um item só
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
            carrinho_local = [dict(i) for i in user_carrinho]

        # 🔹 Funções auxiliares
        def salvar_carrinho():
            page.session.set("carrinho", carrinho_local)
            page.update()

        def calcular_total():
            return sum(i["preco"] * i["quantidade"] for i in carrinho_local)

        total_label = ft.Text(
            f"Total: R$ {calcular_total():.2f}",
            size=22,
            weight="bold",
            color=ft.Colors.AMBER_700
        )

        lista_itens = ft.Column(spacing=12, expand=True)

        # 🔹 Renderiza os itens do carrinho
        def render_lista():
            lista_itens.controls.clear()
            for i in carrinho_local:
                qtd_label = ft.Text(str(i["quantidade"]), size=16, weight="bold", color=ft.Colors.GREY_900)
                subtotal_label = ft.Text(
                    f"Subtotal: R$ {i['preco'] * i['quantidade']:.2f}",
                    color=ft.Colors.GREY_600,
                    size=13
                )

                def alterar_quantidade(e, item=i):
                    item["quantidade"] += e.control.data
                    if item["quantidade"] <= 0:
                        carrinho_local.remove(item)
                    salvar_carrinho()
                    render_lista()
                    lista_itens.update()
                    total_label.value = f"Total: R$ {calcular_total():.2f}"
                    total_label.update()

                card = ft.Container(
                    bgcolor=ft.Colors.WHITE,
                    border_radius=15,
                    padding=15,
                    shadow=ft.BoxShadow(blur_radius=10, spread_radius=1, color=ft.Colors.BLACK12),
                    content=ft.Row(
                        alignment="spaceBetween",
                        vertical_alignment="center",
                        controls=[
                            ft.Column(
                                spacing=3,
                                controls=[
                                    ft.Text(i["nome"], weight="bold", size=18, color=ft.Colors.GREY_900),
                                    ft.Text(f"Preço unitário: R$ {i['preco']:.2f}", size=13, color=ft.Colors.GREY_700),
                                    subtotal_label
                                ]
                            ),
                            ft.Row(
                                spacing=8,
                                alignment="center",
                                controls=[
                                    ft.IconButton(ft.Icons.REMOVE, data=-1, on_click=alterar_quantidade,
                                                  icon_color=ft.Colors.RED_400,
                                                  style=ft.ButtonStyle(shape=ft.CircleBorder())),
                                    qtd_label,
                                    ft.IconButton(ft.Icons.ADD, data=+1, on_click=alterar_quantidade,
                                                  icon_color=ft.Colors.GREEN_400,
                                                  style=ft.ButtonStyle(shape=ft.CircleBorder()))
                                ]
                            )
                        ]
                    )
                )
                lista_itens.controls.append(card)

        render_lista()

        # ================================
        # PAGAMENTO
        # ================================
        pagamento_escolhido = {"metodo": None, "tipo_cartao": None}
        opcoes_pagamento_row = ft.Row(spacing=12, alignment="center")
        cartao_tipos_container = ft.Row(spacing=10, alignment="center", visible=False)

        def card_opcao(texto, cor, selecionado, on_click, icon_name):
            return ft.Container(
                bgcolor=cor if selecionado else ft.Colors.WHITE,
                border=ft.border.all(2, cor if selecionado else ft.Colors.GREY_300),
                border_radius=14,
                padding=ft.padding.symmetric(vertical=10, horizontal=14),
                width=140,
                height=60,
                on_click=on_click,
                content=ft.Row(
                    alignment="center",
                    spacing=8,
                    controls=[
                        ft.Icon(icon_name, color=cor if not selecionado else ft.Colors.WHITE, size=22),
                        ft.Text(
                            texto,
                            size=15,
                            weight="bold",
                            color="white" if selecionado else cor
                        )
                    ]
                ),
                animate=ft.Animation(250, ft.AnimationCurve.EASE_IN_OUT)
            )

        def render_pagamento():
            opcoes_pagamento_row.controls.clear()

            if pagamento_escolhido["metodo"] is None:
                opcoes_pagamento_row.controls.extend([
                    card_opcao("Cartão", ft.Colors.PURPLE, False, lambda e: escolher_pagamento("cartao"),
                               ft.Icons.CREDIT_CARD),
                    card_opcao("Pix", ft.Colors.GREEN, False, lambda e: escolher_pagamento("pix"), ft.Icons.PAID)
                ])
            elif pagamento_escolhido["metodo"] == "cartao":
                opcoes_pagamento_row.controls.append(
                    card_opcao("Cartão", ft.Colors.PURPLE, True, lambda e: escolher_pagamento(None),
                               ft.Icons.CREDIT_CARD)
                )
                cartao_tipos_container.visible = True
            elif pagamento_escolhido["metodo"] == "pix":
                opcoes_pagamento_row.controls.append(
                    card_opcao("Pix", ft.Colors.GREEN, True, lambda e: escolher_pagamento(None), ft.Icons.PAID)
                )
                cartao_tipos_container.visible = False

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
                cartao_tipos_container.controls.extend([
                    card_opcao("Débito", ft.Colors.PURPLE, pagamento_escolhido["tipo_cartao"] == "debito",
                               lambda e: escolher_tipo_cartao("debito"), ft.Icons.ATM),
                    card_opcao("Crédito", ft.Colors.PURPLE, pagamento_escolhido["tipo_cartao"] == "credito",
                               lambda e: escolher_tipo_cartao("credito"), ft.Icons.CREDIT_CARD)
                ])
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
        # VIEW FINAL
        # ================================
        view = ft.View(
            f"/comprar/{item_id}",
            padding=20,
            bgcolor="#fafafa",
            scroll="auto",
            controls=[
                ft.Text("Resumo da Compra", size=24, weight="bold", color=ft.Colors.AMBER_800),
                ft.Divider(height=1),
                lista_itens,
                ft.Container(padding=ft.padding.only(top=10), content=total_label),
                ft.Divider(),
                ft.Text("Forma de pagamento", size=18, weight="bold", color=ft.Colors.GREY_800),
                opcoes_pagamento_row,
                cartao_tipos_container,
                ft.Container(
                    alignment=ft.alignment.center,
                    padding=ft.padding.symmetric(vertical=20),
                    content=ft.ElevatedButton(
                        "Confirmar Compra",
                        on_click=confirmar,
                        bgcolor=ft.Colors.AMBER_600,
                        color=ft.Colors.WHITE,
                        height=52,
                        width=260,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=14))
                    )
                ),
                ft.Row(
                    alignment="center",
                    controls=[
                        ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: go_carrinho(),
                                      icon_color=ft.Colors.GREY_600,
                                      style=ft.ButtonStyle(shape=ft.CircleBorder()))
                    ]
                )
            ]
        )

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
    def go_configs(): page.go("/configs")
    def go_cardapio(): page.go("/cardapio")
    def go_carrinho(): page.go("/carrinho")
    def go_pedidos():
        if page.route.startswith("/comprar") or page.route == "/pagamento":
            page.session.set("last_route", "/cardapio")
        else:
            page.session.set("last_route", page.route)

        page.go("/pedidos")
    def go_editar_usuario(): page.go("/perfil_view")
    def go_comprar(pid): page.go(f"/comprar/{pid}")

    def route_change(route):
        # por padrão, esconde o FAB
        page.floating_action_button = None

        if page.route == "/login":
            page.views.clear(); page.views.append(login_view(page, go_cardapio, go_cadastro, api_request))
        elif page.route == "/cadastro":
            page.views.clear(); page.views.append(cadastro_view(page, go_login, api_request))
        elif page.route == "/menu":
            page.views.clear(); page.views.append(menu_view())
        elif page.route == "/cardapio":
            page.views.clear(); page.views.append(cardapio_view())
        elif page.route == "/carrinho":
            page.views.clear(); page.views.append(carrinho_view())
        elif page.route == "/pedidos":
            page.views.clear(); page.views.append(pedidos_view())
        elif page.route == "/perfil_view":
            page.views.clear(); page.views.append(perfil_view(page, api_request, go_menu, go_pedidos))
        elif page.route.startswith("/comprar/"):
            pid = page.route.split("/")[-1]
            item_id = int(pid) if pid.isdigit() else pid  # aceita "carrinho" também
            page.views.clear()
            page.views.append(comprar_view(item_id))

        page.update()

    page.on_route_change = route_change
    page.go("/login")


ft.app(target=main)