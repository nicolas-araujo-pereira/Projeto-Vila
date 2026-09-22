"""
RPG Isométrico 2D - Protótipo Tkinter (funciona sem pygame)
Mesma ideia do main.py mas usando apenas biblioteca padrão.

Controles:
- WASD / Setas: mover
- E: conversar com Ayla (quando perto, círculo amarelo)
- 1,2,3 ou clique nas opções

Rodar: python main_tk.py
"""
import tkinter as tk
import math

LARGURA, ALTURA = 1000, 680
TILE_W, TILE_H = 64, 32
MAP_W, MAP_H = 10, 10

CORES = {
    "bg_top": "#17212b",
    "bg_bot": "#2a3a4a",
    "grama_claro": "#568e4e",
    "grama_escuro": "#487a42",
    "borda": "#3a6335",
    "agua": "#2d5573",
    "agua_borda": "#3c6e8f",
}

DIALOGO_INICIO = {
    "texto": "Olá, viajante! Não te vi chegando. Você deve ser o novo morador, certo? Eu sou a Ayla, guardiã da vila.",
    "nome": "Ayla",
    "opcoes": [
        ("Sou sim! Acabei de chegar. O que é este lugar?", "apresentacao"),
        ("Talvez... Quem é você?", "quem_e_voce"),
        ("[Ficar em silêncio e observar]", "silencio"),
    ]
}
DIALOGOS = {
    "apresentacao": {
        "texto": "Esta é Vila do Vale Brumado. Um lugar pequeno, mas cheio de histórias. As casas antigas, o lago... dizem que as pedras aqui lembram de tudo que já aconteceu.",
        "nome": "Ayla",
        "opcoes": [("Parece um lugar tranquilo.", "tranquilo"), ("Histórias? Que tipo de histórias?", "historias")]
    },
    "quem_e_voce": {
        "texto": "Eu cuido para que a vila não seja esquecida. Conheço cada trilha, cada morador... e agora, você também faz parte disso.",
        "nome": "Ayla",
        "opcoes": [("Obrigado, Ayla. Quero conhecer melhor.", "tranquilo"), ("Entendi. Nos vemos por aí.", "fim")]
    },
    "silencio": {
        "texto": "(Ayla sorri, paciente) ...Tudo bem. Nem todos gostam de falar de primeira. Ficarei aqui quando quiser conversar.",
        "nome": "Ayla",
        "opcoes": [("Desculpe, só estou um pouco perdido.", "apresentacao"), ("... (continuar em silêncio)", "fim_silencio")]
    },
    "tranquilo": {
        "texto": "Tranquilo sim... quando quer. Mas até o silêncio aqui guarda segredos. Se quiser, posso te mostrar o mirante ao entardecer. É lindo.",
        "nome": "Ayla",
        "opcoes": [("Eu adoraria!", "fim_bom"), ("Vou pensar. Obrigado.", "fim")]
    },
    "historias": {
        "texto": "Dizem que à noite o lago reflete não só as estrelas, mas memórias. Alguns juram ter visto luzes antigas... Mas isso é conversa pra outra hora, não acha?",
        "nome": "Ayla",
        "opcoes": [("Agora fiquei curioso!", "fim_curioso"), ("Talvez seja melhor não mexer com isso...", "fim")]
    },
    "fim": {"texto": "Claro. Estarei por aqui, perto do lago. Quando quiser, é só me procurar. Seja bem-vindo à Vila.", "nome": "Ayla", "opcoes": []},
    "fim_bom": {"texto": "(Ayla sorri) Ótimo! Te encontro lá no fim da tarde então. Vai ser bom ter alguém novo para compartilhar a vista.", "nome": "Ayla", "opcoes": []},
    "fim_curioso": {"texto": "Haha, sabia que diria isso! Então nos vemos em breve. A vila gosta de quem tem curiosidade.", "nome": "Ayla", "opcoes": []},
    "fim_silencio": {"texto": "(Ayla acena com compreensão e volta a olhar o lago) ...", "nome": "Ayla", "opcoes": []},
}

def cart_para_iso(x, y):
    return (x - y) * (TILE_W // 2), (x + y) * (TILE_H // 2)

class Jogo:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=LARGURA, height=ALTURA, bg=CORES["bg_top"], highlightthickness=0)
        self.canvas.pack()

        self.jogador_x, self.jogador_y = 2.5, 2.5
        self.npc_x, self.npc_y = 6, 5
        self.vel = 5.0
        self.teclas = set()

        self.offset_x = LARGURA // 2
        self.offset_y = 110

        self.dialogo_ativo = False
        self.dialogo_atual = DIALOGO_INICIO
        self.dialogo_id = "inicio"
        self.pulso = 0

        root.bind("<KeyPress>", self.on_press)
        root.bind("<KeyRelease>", self.on_release)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.focus_set()

        self.loop()

    def on_press(self, e):
        k = e.keysym.lower()
        self.teclas.add(k)
        if k == "e":
            if not self.dialogo_ativo and self.pode_interagir():
                self.iniciar_dialogo()
            elif self.dialogo_ativo and not self.dialogo_atual["opcoes"]:
                self.dialogo_ativo = False
        elif k == "escape":
            if self.dialogo_ativo and not self.dialogo_atual["opcoes"]:
                self.dialogo_ativo = False
            elif self.dialogo_ativo:
                self.dialogo_ativo = False
            else:
                self.root.quit()
        elif k in ("1", "2", "3"):
            if self.dialogo_ativo:
                idx = int(k)-1
                self.escolher(idx)
        elif k in ("return", "space"):
            if self.dialogo_ativo and not self.dialogo_atual["opcoes"]:
                self.dialogo_ativo = False

    def on_release(self, e):
        k = e.keysym.lower()
        self.teclas.discard(k)

    def on_click(self, e):
        if not self.dialogo_ativo:
            return
        # verifica clique nas opções desenhadas
        for (x1, y1, x2, y2, idx) in getattr(self, "botoes", []):
            if x1 <= e.x <= x2 and y1 <= e.y <= y2:
                if not self.dialogo_atual["opcoes"]:
                    self.dialogo_ativo = False
                else:
                    self.escolher(idx)
                break

    def pode_interagir(self):
        return abs(self.jogador_x - self.npc_x) + abs(self.jogador_y - self.npc_y) < 1.8

    def iniciar_dialogo(self):
        self.dialogo_ativo = True
        self.dialogo_id = "inicio"
        self.dialogo_atual = DIALOGO_INICIO

    def escolher(self, idx):
        if idx < 0 or idx >= len(self.dialogo_atual["opcoes"]):
            return
        _, prox = self.dialogo_atual["opcoes"][idx]
        if prox in DIALOGOS:
            self.dialogo_id = prox
            self.dialogo_atual = DIALOGOS[prox]
        else:
            self.dialogo_ativo = False

    def update(self):
        if self.dialogo_ativo:
            return
        dx = dy = 0
        if "w" in self.teclas or "up" in self.teclas:
            dy -= 1; dx -= 1
        if "s" in self.teclas or "down" in self.teclas:
            dy += 1; dx += 1
        if "a" in self.teclas or "left" in self.teclas:
            dx -= 1; dy += 1
        if "d" in self.teclas or "right" in self.teclas:
            dx += 1; dy -= 1
        if dx or dy:
            norm = math.hypot(dx, dy)
            dx /= norm; dy /= norm
            dt = 1/60
            nx = max(0.5, min(MAP_W-0.5, self.jogador_x + dx * self.vel * dt))
            ny = max(0.5, min(MAP_H-0.5, self.jogador_y + dy * self.vel * dt))
            if math.hypot(nx - self.npc_x, ny - self.npc_y) < 0.9:
                ang = math.atan2(ny - self.npc_y, nx - self.npc_x)
                nx = self.npc_x + math.cos(ang)*0.9
                ny = self.npc_y + math.sin(ang)*0.9
            self.jogador_x, self.jogador_y = nx, ny

    def desenhar(self):
        c = self.canvas
        c.delete("all")
        # fundo
        for y in range(ALTURA):
            t = y/ALTURA
            r = int(23 + t*15)
            g = int(33 + t*20)
            b = int(43 + t*25)
            c.create_line(0, y, LARGURA, y, fill=f"#{r:02x}{g:02x}{b:02x}")

        # tiles
        for y in range(MAP_H):
            for x in range(MAP_W):
                cx, cy = cart_para_iso(x, y)
                cx += self.offset_x; cy += self.offset_y
                claro = (x+y)%2==0
                cor = CORES["grama_claro"] if claro else CORES["grama_escuro"]
                if x>=7 and y>=7:
                    cor = CORES["agua"]
                pts = [cx, cy, cx+32, cy+16, cx, cy+32, cx-32, cy+16]
                c.create_polygon(pts, fill=cor, outline=CORES["borda"])
                if x>=7 and y>=7 and (x==7 or y==7):
                    c.create_polygon(pts, fill="", outline=CORES["agua_borda"], width=2)

        # personagens em ordem de profundidade
        objs = sorted([(self.npc_x+self.npc_y, "npc"), (self.jogador_x+self.jogador_y, "player")])
        for _, tipo in objs:
            if tipo == "npc":
                self.desenhar_personagem(self.npc_x, self.npc_y, "#ffb43c", "Ayla", is_npc=True)
            else:
                self.desenhar_personagem(self.jogador_x, self.jogador_y, "#5090ff", "Você", is_npc=False)

        # hint
        if self.pode_interagir() and not self.dialogo_ativo:
            cx, cy = cart_para_iso(self.npc_x, self.npc_y)
            cx += self.offset_x; cy += self.offset_y - 68
            c.create_rectangle(cx-88, cy-10, cx+88, cy+12, fill="black", outline="", stipple="gray50")
            c.create_text(cx, cy, text="Pressione [E] para conversar", fill="white", font=("Segoe UI", 9))
            # pulso
            r = 20 + 3*math.sin(self.pulso*0.15)
            c.create_oval(cx- r, cy-38 -r, cx+ r, cy-38 +r, outline="#ffcd50", width=2)
            c.create_oval(cx-4, cy-42, cx+4, cy-34, fill="#ffcd50", outline="")

        # HUD topo
        c.create_rectangle(0,0, LARGURA, 52, fill="black", stipple="gray50", outline="")
        c.create_rectangle(0,0, LARGURA, 52, fill="", outline="#333333")
        c.create_text(20, 14, text="VILA DO VALE BRUMADO — Protótipo", fill="white", font=("Segoe UI", 11, "bold"), anchor="w")
        c.create_text(20, 32, text="RPG de escolhas  •  Isométrico  •  WASD para mover  •  E para interagir", fill="#b0b0b0", font=("Segoe UI", 8), anchor="w")

        # diálogo
        self.botoes = []
        if self.dialogo_ativo:
            self.desenhar_dialogo()

        self.pulso += 1

    def desenhar_personagem(self, gx, gy, cor, nome, is_npc=False):
        c = self.canvas
        cx, cy = cart_para_iso(gx, gy)
        cx += self.offset_x; cy += self.offset_y + 16
        # sombra
        c.create_oval(cx-18, cy+8, cx+18, cy+20, fill="#000000", stipple="gray50", outline="")
        # pernas
        c.create_rectangle(cx-8, cy-2, cx-2, cy+12, fill="#1a1a2a", outline="")
        c.create_rectangle(cx+2, cy-2, cx+8, cy+12, fill="#1a1a2a", outline="")
        # tronco
        c.create_rectangle(cx-12, cy-28, cx+12, cy-2, fill=cor, outline="#333", width=1)
        # cabeça
        c.create_oval(cx-11, cy-42, cx+11, cy-20, fill="#ebd2b4", outline="#8a7060")
        cabelo = "#2b2118" if not is_npc else "#785033"
        c.create_arc(cx-11, cy-44, cx+11, cy-24, start=0, extent=180, fill=cabelo, outline=cabelo, width=4, style="arc")
        c.create_oval(cx-4, cy-32, cx-2, cy-30, fill="black")
        c.create_oval(cx+2, cy-32, cx+4, cy-30, fill="black")
        # nome
        c.create_rectangle(cx-28, cy+20, cx+28, cy+34, fill="black", outline="")
        c.create_text(cx, cy+27, text=nome, fill="white", font=("Segoe UI", 7, "bold"))

    def desenhar_dialogo(self):
        c = self.canvas
        # overlay
        c.create_rectangle(0,0, LARGURA, ALTURA, fill="black", stipple="gray50")
        box_w, box_h = 760, 250
        box_x = (LARGURA - box_w)//2
        box_y = ALTURA - box_h - 20
        # caixa
        c.create_rectangle(box_x-4, box_y-4, box_x+box_w+4, box_y+box_h+4, fill="#000000", outline="", stipple="gray50")
        c.create_rectangle(box_x, box_y, box_x+box_w, box_y+box_h, fill="#1c2028", outline="#464b55", width=2)
        # tag nome
        nome = self.dialogo_atual.get("nome", "")
        if nome:
            c.create_rectangle(box_x+20, box_y-12, box_x+110, box_y+10, fill="#ffcd50", outline="")
            c.create_text(box_x+65, box_y-1, text=nome.upper(), fill="#1a1a1a", font=("Segoe UI", 8, "bold"))
        # texto com quebra
        texto = self.dialogo_atual["texto"]
        # quebra manual ~70 chars
        linhas = []
        palavras = texto.split(" ")
        linha=""
        for p in palavras:
            teste = linha + (" " if linha else "") + p
            # estimativa largura: ~7px por char
            if len(teste)*7 > box_w - 48:
                linhas.append(linha)
                linha = p
            else:
                linha = teste
        if linha: linhas.append(linha)
        y = box_y + 28
        for lin in linhas:
            c.create_text(box_x+24, y, text=lin, fill="white", font=("Segoe UI", 10), anchor="w")
            y += 20
        y += 10
        c.create_line(box_x+24, y, box_x+box_w-24, y, fill="#3a3f4a")
        y += 14
        opcoes = self.dialogo_atual["opcoes"]
        if opcoes:
            for i, (opt, _) in enumerate(opcoes):
                rect_x1, rect_y1 = box_x+24, y
                rect_x2, rect_y2 = box_x+box_w-24, y+30
                c.create_rectangle(rect_x1, rect_y1, rect_x2, rect_y2, fill="#262a34", outline="#5a5f6e", width=1)
                c.create_text(rect_x1+10, rect_y1+15, text=str(i+1), fill="#ffcd50", font=("Segoe UI", 9, "bold"), anchor="w")
                c.create_text(rect_x1+28, rect_y1+15, text=opt, fill="white", font=("Segoe UI", 9), anchor="w")
                self.botoes.append((rect_x1, rect_y1, rect_x2, rect_y2, i))
                y += 36
        else:
            c.create_text(box_x+24, y, text="Pressione [ESC] ou [ENTER] para fechar", fill="#a0a0a0", font=("Segoe UI", 8), anchor="w")
            rx1, ry1 = box_x+box_w-120, box_y+box_h-36
            rx2, ry2 = rx1+96, ry1+24
            c.create_rectangle(rx1, ry1, rx2, ry2, fill="#ffcd50", outline="")
            c.create_text((rx1+rx2)//2, (ry1+ry2)//2, text="Fechar [ESC]", fill="#1a1a1a", font=("Segoe UI", 8, "bold"))
            self.botoes.append((rx1, ry1, rx2, ry2, -1))
            y += 30

    def loop(self):
        self.update()
        self.desenhar()
        self.root.after(16, self.loop)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Projeto Vila - Protótipo Isométrico (Tkinter)")
    root.resizable(False, False)
    Jogo(root)
    root.mainloop()
