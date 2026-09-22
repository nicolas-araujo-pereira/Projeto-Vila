"""
RPG Isométrico 2D - Protótipo de Visualização
Protagonista + NPC com conversa de apresentação com escolhas

Controles:
- WASD / Setas: mover protagonista
- E: interagir com NPC (quando perto)
- 1,2,3 ou Mouse: escolher opção de diálogo
- ESC: fechar diálogo / sair

Requisitos: pip install pygame
Rodar: python main.py
"""

import pygame
import sys
import math

# --- Configurações ---
LARGURA, ALTURA = 1280, 720
FPS = 60

TILE_W, TILE_H = 64, 32  # tamanho do tile isométrico
MAP_W, MAP_H = 10, 10

CORES = {
    "bg": (23, 33, 43),
    "grama_claro": (86, 142, 78),
    "grama_escuro": (72, 122, 66),
    "grama_borda": (58, 99, 53),
    "agua": (45, 85, 115),
    "player": (80, 140, 255),
    "player_sombra": (50, 90, 180),
    "npc": (255, 180, 60),
    "npc_sombra": (180, 120, 30),
    "texto": (240, 240, 235),
    "texto_sec": (180, 180, 175),
    "caixa": (28, 32, 40),
    "caixa_borda": (70, 75, 85),
    "escolha_hover": (45, 50, 65),
    "escolha_borda": (90, 95, 110),
    "destaque": (255, 205, 80),
}

pygame.init()
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Projeto Vila - Protótipo Isométrico")
clock = pygame.time.Clock()

font_titulo = pygame.font.SysFont("segoe ui", 22, bold=True)
font_texto = pygame.font.SysFont("segoe ui", 18)
font_texto_bold = pygame.font.SysFont("segoe ui", 18, bold=True)
font_pequena = pygame.font.SysFont("segoe ui", 14)
font_nome = pygame.font.SysFont("segoe ui", 13, bold=True)

# --- Funções Isométricas ---
def cart_para_iso(x, y):
    """Converte coordenada cartesiana do grid para tela isométrica"""
    iso_x = (x - y) * (TILE_W // 2)
    iso_y = (x + y) * (TILE_H // 2)
    return iso_x, iso_y

def desenhar_tile(surf, ox, oy, gx, gy, cor):
    cx, cy = cart_para_iso(gx, gy)
    cx += ox
    cy += oy
    pontos = [
        (cx, cy),
        (cx + TILE_W // 2, cy + TILE_H // 2),
        (cx, cy + TILE_H),
        (cx - TILE_W // 2, cy + TILE_H // 2),
    ]
    pygame.draw.polygon(surf, cor, pontos)
    pygame.draw.polygon(surf, CORES["grama_borda"], pontos, 1)
    # brilho topo
    brilho = [(cx, cy), (cx + TILE_W // 2, cy + TILE_H // 2), (cx, cy + TILE_H // 2 - 4), (cx - TILE_W // 2, cy + TILE_H // 2)]
    # simples detalhe
    if (gx + gy) % 3 == 0:
        pygame.draw.circle(surf, (95, 155, 88), (cx, cy + TILE_H//2), 2)

def desenhar_personagem(surf, ox, oy, gx, gy, cor, cor_sombra, nome, selecionavel=False, pulso=0):
    cx, cy = cart_para_iso(gx, gy)
    cx += ox
    cy += oy + TILE_H // 2

    # sombra no chão
    pygame.draw.ellipse(surf, (0, 0, 0, 60), pygame.Rect(cx - 18, cy + 8, 36, 12))
    # sombra colorida oval
    s = pygame.Surface((36, 12), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (*cor_sombra, 90), (0, 0, 36, 12))
    surf.blit(s, (cx - 18, cy + 8))

    # indicador se pode interagir
    if selecionavel:
        alpha = int(120 + 80 * math.sin(pulso * 0.008))
        r = 22 + int(3 * math.sin(pulso * 0.008))
        pygame.draw.circle(surf, (255, 255, 255, alpha), (cx, cy - 38), r, 2)
        pygame.draw.circle(surf, CORES["destaque"], (cx, cy - 38), 4)

    # corpo (losango + retângulo arredondado simulado)
    # pernas
    pygame.draw.rect(surf, (30, 30, 45), (cx - 8, cy - 2, 6, 14), border_radius=3)
    pygame.draw.rect(surf, (30, 30, 45), (cx + 2, cy - 2, 6, 14), border_radius=3)
    # tronco
    pygame.draw.rect(surf, cor, (cx - 12, cy - 28, 24, 24), border_radius=6)
    pygame.draw.rect(surf, (255, 255, 255, 40), (cx - 12, cy - 28, 24, 8), border_radius=6)
    # cabeça
    pygame.draw.circle(surf, (235, 210, 180), (cx, cy - 32), 11)
    pygame.draw.circle(surf, (210, 180, 150), (cx, cy - 32), 11, 1)
    # cabelo
    pygame.draw.circle(surf, (45, 35, 30) if cor == CORES["player"] else (120, 80, 50), (cx, cy - 38), 11, 4)
    # olhos
    pygame.draw.circle(surf, (30, 30, 30), (cx - 4, cy - 32), 1.5)
    pygame.draw.circle(surf, (30, 30, 30), (cx + 4, cy - 32), 1.5)

    # nome
    txt = font_nome.render(nome, True, (255, 255, 255))
    bg = pygame.Surface((txt.get_width()+10, txt.get_height()+4), pygame.SRCALPHA)
    bg.fill((0,0,0,120))
    surf.blit(bg, (cx - bg.get_width()//2, cy + 22))
    tela.blit(txt, (cx - txt.get_width()//2, cy + 24))

    return cx, cy

# --- Diálogo ---
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
        "opcoes": [
            ("Parece um lugar tranquilo.", "tranquilo"),
            ("Histórias? Que tipo de histórias?", "historias"),
        ]
    },
    "quem_e_voce": {
        "texto": "Eu cuido para que a vila não seja esquecida. Conheço cada trilha, cada morador... e agora, você também faz parte disso. Se precisar, estarei por aqui.",
        "nome": "Ayla",
        "opcoes": [
            ("Obrigado, Ayla. Quero conhecer melhor.", "tranquilo"),
            ("Entendi. Nos vemos por aí.", "fim"),
        ]
    },
    "silencio": {
        "texto": "(Ayla sorri, paciente) ...Tudo bem. Nem todos gostam de falar de primeira. Ficarei aqui quando quiser conversar. A vila tem seu próprio ritmo.",
        "nome": "Ayla",
        "opcoes": [
            ("Desculpe, só estou um pouco perdido.", "apresentacao"),
            ("... (continuar em silêncio)", "fim_silencio"),
        ]
    },
    "tranquilo": {
        "texto": "Tranquilo sim... quando quer. Mas até o silêncio aqui guarda segredos. Se quiser, posso te mostrar o mirante ao entardecer. É lindo.",
        "nome": "Ayla",
        "opcoes": [
            ("Eu adoraria!", "fim_bom"),
            ("Vou pensar. Obrigado.", "fim"),
        ]
    },
    "historias": {
        "texto": "Dizem que à noite o lago reflete não só as estrelas, mas memórias. Alguns juram ter visto luzes antigas... Mas isso... é conversa pra outra hora, não acha?",
        "nome": "Ayla",
        "opcoes": [
            ("Agora fiquei curioso!", "fim_curioso"),
            ("Talvez seja melhor não mexer com isso...", "fim"),
        ]
    },
    "fim": {
        "texto": "Claro. Estarei por aqui, perto do lago. Quando quiser, é só me procurar. Seja bem-vindo à Vila.",
        "nome": "Ayla",
        "opcoes": []
    },
    "fim_bom": {
        "texto": "(Ayla sorri) Ótimo! Te encontro lá no fim da tarde então. Vai ser bom ter alguém novo para compartilhar a vista.",
        "nome": "Ayla",
        "opcoes": []
    },
    "fim_curioso": {
        "texto": "Haha, sabia que diria isso! Então nos vemos em breve. A vila gosta de quem tem curiosidade. Só não vá se perder nas trilhas antigas sem mim, hein?",
        "nome": "Ayla",
        "opcoes": []
    },
    "fim_silencio": {
        "texto": "(Ayla acena com compreensão e volta a olhar o lago) ...",
        "nome": "Ayla",
        "opcoes": []
    },
}

class Jogo:
    def __init__(self):
        # posição no grid (float para movimento suave)
        self.jogador_x = 2.5
        self.jogador_y = 2.5
        self.npc_x = 6
        self.npc_y = 5
        self.vel = 3.0  # tiles por segundo

        self.dialogo_ativo = False
        self.dialogo_id = "inicio"
        self.dialogo_atual = DIALOGO_INICIO
        self.escolha_hover = -1

        # câmera isométrica centralizada
        self.offset_x = LARGURA // 2
        self.offset_y = 120

        self.tempo = 0

    def pode_interagir(self):
        dist = abs(self.jogador_x - self.npc_x) + abs(self.jogador_y - self.npc_y)
        # distância manhattan < 1.8
        return dist < 1.8

    def iniciar_dialogo(self):
        self.dialogo_ativo = True
        self.dialogo_id = "inicio"
        self.dialogo_atual = DIALOGO_INICIO

    def escolher(self, idx):
        if idx < 0 or idx >= len(self.dialogo_atual["opcoes"]):
            return
        _, proximo = self.dialogo_atual["opcoes"][idx]
        if proximo in DIALOGOS:
            self.dialogo_id = proximo
            self.dialogo_atual = DIALOGOS[proximo]
        else:
            self.dialogo_ativo = False
        # se for fim sem opções, fecha no próximo clique/enter
        if len(self.dialogo_atual["opcoes"]) == 0:
            # fica mostrando a última fala até apertar ESC/ENTER/E
            pass

    def update(self, dt, teclas):
        if self.dialogo_ativo:
            return
        dx = 0
        dy = 0
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            dy -= 1
            dx -= 1
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            dy += 1
            dx += 1
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            dx -= 1
            dy += 1
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            dx += 1
            dy -= 1

        if dx != 0 or dy != 0:
            norm = math.hypot(dx, dy)
            dx /= norm
            dy /= norm
            nx = self.jogador_x + dx * self.vel * dt
            ny = self.jogador_y + dy * self.vel * dt
            # limites do mapa
            nx = max(0.5, min(MAP_W - 0.5, nx))
            ny = max(0.5, min(MAP_H - 0.5, ny))
            # colisão simples com NPC (não atravessar)
            if math.hypot(nx - self.npc_x, ny - self.npc_y) < 0.9:
                # empurra pra fora
                ang = math.atan2(ny - self.npc_y, nx - self.npc_x)
                nx = self.npc_x + math.cos(ang) * 0.9
                ny = self.npc_y + math.sin(ang) * 0.9
            self.jogador_x = nx
            self.jogador_y = ny

    def desenhar_mundo(self):
        # fundo degradê
        for y in range(ALTURA):
            t = y / ALTURA
            r = int(23 + t * 12)
            g = int(33 + t * 18)
            b = int(43 + t * 20)
            pygame.draw.line(tela, (r, g, b), (0, y), (LARGURA, y))

        # tiles do chão
        for y in range(MAP_H):
            for x in range(MAP_W):
                # variação xadrez
                claro = (x + y) % 2 == 0
                cor = CORES["grama_claro"] if claro else CORES["grama_escuro"]
                # lago no canto inferior
                if x >= 7 and y >= 7:
                    cor = CORES["agua"]
                desenhar_tile(tela, self.offset_x, self.offset_y, x, y, cor)

        # borda do lago
        for x in range(7, 10):
            for y in range(7, 10):
                if x == 7 or y == 7:
                    cx, cy = cart_para_iso(x, y)
                    cx += self.offset_x
                    cy += self.offset_y
                    pygame.draw.polygon(tela, (60, 110, 140), [
                        (cx, cy+2), (cx+32, cy+18), (cx, cy+34), (cx-32, cy+18)
                    ], 2)

        # desenhar personagens em ordem de profundidade (y+x)
        objetos = [
            (self.npc_x + self.npc_y, "npc"),
            (self.jogador_x + self.jogador_y, "player"),
        ]
        objetos.sort(key=lambda o: o[0])

        for _, tipo in objetos:
            if tipo == "npc":
                desenhar_personagem(tela, self.offset_x, self.offset_y, self.npc_x, self.npc_y,
                                    CORES["npc"], CORES["npc_sombra"], "Ayla",
                                    selecionavel=self.pode_interagir() and not self.dialogo_ativo,
                                    pulso=self.tempo)
            else:
                desenhar_personagem(tela, self.offset_x, self.offset_y, self.jogador_x, self.jogador_y,
                                    CORES["player"], CORES["player_sombra"], "Você")

        # hint de interação
        if self.pode_interagir() and not self.dialogo_ativo:
            txt = font_pequena.render("Pressione [E] para conversar", True, (255, 255, 255))
            bg = pygame.Surface((txt.get_width()+12, txt.get_height()+6), pygame.SRCALPHA)
            bg.fill((0,0,0,160))
            # posição acima do NPC
            cx, cy = cart_para_iso(self.npc_x, self.npc_y)
            cx += self.offset_x
            cy += self.offset_y - 65
            tela.blit(bg, (cx - bg.get_width()//2, cy))
            tela.blit(txt, (cx - txt.get_width()//2, cy+3))

    def desenhar_hud(self):
        # título topo
        titulo = font_titulo.render("VILA DO VALE BRUMADO — Protótipo", True, CORES["texto"])
        subt = font_pequena.render("RPG de escolhas  •  Câmera isométrica  •  WASD para mover", True, CORES["texto_sec"])
        pygame.draw.rect(tela, (0,0,0,100), (0,0,LARGURA,56))
        s = pygame.Surface((LARGURA,56), pygame.SRCALPHA)
        s.fill((0,0,0,110))
        tela.blit(s, (0,0))
        tela.blit(titulo, (24, 10))
        tela.blit(subt, (24, 32))
        # minimapa texto
        fps_txt = font_pequena.render(f"FPS: {int(clock.get_fps())}", True, CORES["texto_sec"])
        tela.blit(fps_txt, (LARGURA - fps_txt.get_width() - 20, 20))

    def desenhar_dialogo(self, mouse_pos):
        if not self.dialogo_ativo:
            return []

        # overlay escurecido
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0,0,0,90))
        tela.blit(overlay, (0,0))

        # caixa de diálogo
        box_w, box_h = 860, 300
        box_x = (LARGURA - box_w)//2
        box_y = ALTURA - box_h - 28
        radius = 14

        # sombra
        sombra = pygame.Surface((box_w+12, box_h+12), pygame.SRCALPHA)
        pygame.draw.rect(sombra, (0,0,0,80), (0,0,box_w+12, box_h+12), border_radius=radius+6)
        tela.blit(sombra, (box_x-6, box_y-6))

        pygame.draw.rect(tela, CORES["caixa"], (box_x, box_y, box_w, box_h), border_radius=radius)
        pygame.draw.rect(tela, CORES["caixa_borda"], (box_x, box_y, box_w, box_h), 2, border_radius=radius)

        # nome do falante
        nome = self.dialogo_atual.get("nome", "")
        if nome:
            tag_w = 110
            pygame.draw.rect(tela, CORES["destaque"], (box_x+24, box_y-14, tag_w, 24), border_radius=8)
            nt = font_nome.render(nome.upper(), True, (30,30,30))
            tela.blit(nt, (box_x+24 + (tag_w - nt.get_width())//2, box_y-10))

        # texto
        texto = self.dialogo_atual["texto"]
        # quebra de linha simples
        palavras = texto.split(" ")
        linhas = []
        linha_atual = ""
        for p in palavras:
            teste = linha_atual + (" " if linha_atual else "") + p
            if font_texto.size(teste)[0] > box_w - 48:
                linhas.append(linha_atual)
                linha_atual = p
            else:
                linha_atual = teste
        if linha_atual:
            linhas.append(linha_atual)

        y_txt = box_y + 28
        for lin in linhas:
            t = font_texto.render(lin, True, CORES["texto"])
            tela.blit(t, (box_x+24, y_txt))
            y_txt += 24

        # opções
        rects = []
        opcoes = self.dialogo_atual["opcoes"]
        if opcoes:
            y_txt += 14
            pygame.draw.line(tela, CORES["caixa_borda"], (box_x+24, y_txt), (box_x+box_w-24, y_txt), 1)
            y_txt += 14
            for i, (opt, _) in enumerate(opcoes):
                r = pygame.Rect(box_x+24, y_txt, box_w-48, 32)
                hover = r.collidepoint(mouse_pos)
                if hover:
                    self.escolha_hover = i
                cor_fundo = CORES["escolha_hover"] if hover else (38, 42, 52)
                borda = CORES["destaque"] if hover else CORES["escolha_borda"]
                pygame.draw.rect(tela, cor_fundo, r, border_radius=8)
                pygame.draw.rect(tela, borda, r, 1, border_radius=8)
                num = font_texto_bold.render(f"{i+1}", True, CORES["destaque"] if hover else CORES["texto_sec"])
                tela.blit(num, (r.x+12, r.y+6))
                txt = font_texto.render(opt, True, CORES["texto"])
                tela.blit(txt, (r.x+32, r.y+6))
                rects.append(r)
                y_txt += 40
        else:
            # fim: instrução
            y_txt += 18
            hint = font_pequena.render("Pressione [ESC] ou [ENTER] para fechar  •  [E] para falar novamente", True, CORES["texto_sec"])
            tela.blit(hint, (box_x+24, y_txt))
            # botão fechar
            r = pygame.Rect(box_x+box_w-140, box_y+box_h-42, 116, 28)
            pygame.draw.rect(tela, CORES["destaque"], r, border_radius=8)
            t = font_texto_bold.render("Fechar [ESC]", True, (30,30,30))
            tela.blit(t, (r.centerx - t.get_width()//2, r.centery - t.get_height()//2))
            rects.append(r)

        return rects


def main():
    jogo = Jogo()
    rodando = True
    mouse_pos = (0,0)

    while rodando:
        dt = clock.tick(FPS) / 1000.0
        jogo.tempo += dt * 1000

        mouse_pos = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    if jogo.dialogo_ativo:
                        # se for diálogo com opções, ESC não fecha, só nos finais
                        if len(jogo.dialogo_atual["opcoes"]) == 0:
                            jogo.dialogo_ativo = False
                        # alternativa: ESC fecha qualquer diálogo
                        # jogo.dialogo_ativo = False
                    else:
                        rodando = False
                elif evento.key == pygame.K_e:
                    if not jogo.dialogo_ativo and jogo.pode_interagir():
                        jogo.iniciar_dialogo()
                    elif jogo.dialogo_ativo and len(jogo.dialogo_atual["opcoes"]) == 0:
                        jogo.dialogo_ativo = False
                elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if jogo.dialogo_ativo and len(jogo.dialogo_atual["opcoes"]) == 0:
                        jogo.dialogo_ativo = False
                elif evento.key in (pygame.K_1, pygame.K_KP1):
                    if jogo.dialogo_ativo:
                        jogo.escolher(0)
                elif evento.key in (pygame.K_2, pygame.K_KP2):
                    if jogo.dialogo_ativo:
                        jogo.escolher(1)
                elif evento.key in (pygame.K_3, pygame.K_KP3):
                    if jogo.dialogo_ativo:
                        jogo.escolher(2)
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if jogo.dialogo_ativo:
                    # verificar clique nas opções
                    # redesenha rects para hit test (recalcula)
                    # truque: vamos usar as rects retornadas no frame anterior?
                    # Para simplificar, recalcular aqui rapidamente
                    # Em vez disso, deixamos o desenhar_dialogo retornar rects e testamos no próximo loop.
                    # Aqui fazemos hit test direto chamando lógica de desenho sem desenhar
                    box_w, box_h = 860, 300
                    box_x = (LARGURA - box_w)//2
                    box_y = ALTURA - box_h - 28
                    # reconstruir y
                    texto = jogo.dialogo_atual["texto"]
                    palavras = texto.split(" ")
                    linhas = []
                    la = ""
                    for p in palavras:
                        teste = la + (" " if la else "") + p
                        if font_texto.size(teste)[0] > box_w - 48:
                            linhas.append(la)
                            la = p
                        else:
                            la = teste
                    if la:
                        linhas.append(la)
                    y_txt = box_y + 28 + len(linhas)*24 + 14 + 14
                    opcoes = jogo.dialogo_atual["opcoes"]
                    if opcoes:
                        for i in range(len(opcoes)):
                            r = pygame.Rect(box_x+24, y_txt, box_w-48, 32)
                            if r.collidepoint(evento.pos):
                                jogo.escolher(i)
                                break
                            y_txt += 40
                    else:
                        r = pygame.Rect(box_x+box_w-140, box_y+box_h-42, 116, 28)
                        if r.collidepoint(evento.pos):
                            jogo.dialogo_ativo = False

        teclas = pygame.key.get_pressed()
        jogo.update(dt, teclas)

        jogo.desenhar_mundo()
        jogo.desenhar_hud()
        jogo.desenhar_dialogo(mouse_pos)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
