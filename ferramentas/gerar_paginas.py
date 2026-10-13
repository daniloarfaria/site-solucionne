#!/usr/bin/env python3
"""Gera todas as páginas HTML de public/ a partir deste arquivo.

Uso, na raiz do projeto:
  python3 ferramentas/gerar_paginas.py

Por que um gerador: cabeçalho, rodapé, popup do WhatsApp e ícones são iguais em todas as páginas.
Aqui eles existem uma vez só. Para mudar um texto, edite os dados abaixo (EMPRESA, PRODUTOS, FAQ...)
e rode o comando de novo. Não edite os .html de public/ à mão: a próxima geração sobrescreve.

Imagens: rode antes ferramentas/otimizar_imagens.py (ele gera ferramentas/imagens.json, usado aqui).
"""
import html
import json
from PIL import Image
import os
import re
from datetime import date
from urllib.parse import quote

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(RAIZ, 'public')
ICONES = os.path.join(RAIZ, 'ferramentas', 'icones')
with open(os.path.join(RAIZ, 'ferramentas', 'imagens.json')) as f:
    IMAGENS = json.load(f)

HOJE = date.today().isoformat()
VERSAO_ICONE = 2  # aumente quando o favicon mudar (o navegador guarda o antigo em cache)

# =====================================================================
# Dados da empresa (NAP igual ao Google Meu Negócio)
# =====================================================================
EMPRESA = {
    'nome': 'Solucionne',
    'nome_completo': 'Solucionne – Termo Acústico do Brasil',
    'dominio': 'solucionne.com.br',
    'descricao_curta': 'Soluções acústicas de alta performance para ambientes residenciais, comerciais e industriais.',
    'rua': 'R. Piraí, 269',
    'bairro': 'Concórdia',
    'cidade': 'Belo Horizonte',
    'uf': 'MG',
    'cep': '31110-750',
    'telefone': '(31) 3442-1713',
    'telefone_link': '+553134421713',
    'whatsapp': '553134421713',
    'email': 'vendas@solucionne.com.br',
    'redes': [
        ('Instagram', 'instagram', 'https://www.instagram.com/solucionneacustico/'),
        ('Facebook', 'facebook', 'https://www.facebook.com/solucionneacustico'),
        ('LinkedIn', 'linkedin', 'https://br.linkedin.com/company/solucionneacustico'),
        ('Pinterest', 'pinterest', 'https://www.pinterest.com/solucionneacustico/'),
    ],
}
E = EMPRESA
URL = f"https://{E['dominio']}"
ENDERECO = f"{E['rua']} – {E['bairro']}, {E['cidade']} – {E['uf']}, {E['cep']}"
ROTA = 'https://www.google.com/maps/dir/?api=1&destination=' + quote(f"{E['rua']}, {E['bairro']}, {E['cidade']} - {E['uf']}, {E['cep']}")


def whats(texto):
    return f"https://wa.me/{E['whatsapp']}?text={quote(texto)}"


# =====================================================================
# Produtos (textos do site; cada um vira /<slug>)
# =====================================================================
PRODUTOS = [
    {
        'slug': 'difusores-acusticos', 'nome': 'Difusores Acústicos', 'card': 'difusores-acusticos',
        'titulo': 'Difusores Acústicos para Estúdios e Home Cinema | Solucionne',
        'descricao': 'Difusores acústicos em madeira, EPS e acrílico para estúdios, home cinemas e auditórios. Som natural, sem ecos. Projeto e instalação.',
        'h1': 'Som com qualidade de estúdio: descubra os <em>Difusores Acústicos</em>',
        'lead': 'Controle as reflexões sonoras e garanta um som natural e cristalino em seu ambiente, sem perder a vivacidade acústica.',
        'checks': ['Cria um campo sonoro homogêneo e natural.', 'Evita ecos flutuantes e distorções.', 'Peças com design sofisticado que valorizam o ambiente.'],
        'img': 'difusores-acusticos', 'img_alt': 'Parede revestida com difusores acústicos em relevo',
        'problema': 'O som do seu ambiente parece “embolado” ou sem vida?',
        'solucao': 'A qualidade do som pode ser distorcida por ecos e reflexos de interferência. Para manter o campo sonoro natural, é preferível usar a difusão. Nossos difusores controlam essas interferências, espalhando o som de forma equilibrada, mesmo em ambientes já tratados com absorvedores.',
        'aplicacoes_titulo': 'Perfeito para ambientes críticos',
        'aplicacoes': [('mic', 'Estúdios de Gravação'), ('film', 'Home Cinemas'), ('presentation', 'Auditórios e Teatros'), ('music', 'Salas de Audição Hi-Fi')],
        'specs_titulo': 'Especificações técnicas',
        'specs': [('Material', 'Madeira, EPS, acrílico e outros materiais nobres.'), ('Dimensões padrão', '60x60 cm, 120x60 cm (projetos customizáveis).'), ('Acabamento', 'Natural, pintura em diversas cores ou verniz.'), ('Faixa de atuação', 'Médias e altas frequências.')],
    },
    {
        'slug': 'espumas-acusticas', 'nome': 'Espumas Acústicas', 'card': 'espumas-acusticas',
        'titulo': 'Espumas Acústicas: fim do eco em estúdios e escritórios | Solucionne',
        'descricao': 'Espumas acústicas de 25 a 70 mm, cinza chumbo ou branco gelo, para estúdios, home offices e salas de reunião. Menos eco e som mais limpo.',
        'h1': 'Elimine ecos e ruídos com as <em>Espumas Acústicas</em> Solucionne',
        'lead': 'Transforme qualquer ambiente em um espaço com som de qualidade profissional, conforto acústico e um visual moderno.',
        'checks': ['Melhora a clareza de áudios e conversas.', 'Reduz a reverberação e o barulho excessivo.', 'Design moderno que decora seu ambiente.'],
        'img': 'espumas-acusticas', 'img_alt': 'Espumas acústicas instaladas em ambiente moderno',
        'problema': 'Seu ambiente sofre com ecos e ruídos indesejados?',
        'solucao': 'As espumas acústicas da Solucionne são absorvedores sonoros que proporcionam conforto acústico e um acabamento estético superior para qualquer espaço fechado.',
        'aplicacoes_titulo': 'Ideal para diversos ambientes',
        'aplicacoes': [('mic', 'Estúdios'), ('monitor', 'Home Offices'), ('users', 'Salas de Reunião'), ('film', 'Home Cinema')],
        'extra': 'espumas',
    },
    {
        'slug': 'forro-acustico', 'nome': 'Forro Acústico', 'card': 'forro-acustico-com-amortecedor',
        'titulo': 'Forro Acústico com Amortecedor: menos eco e ruído | Solucionne',
        'descricao': 'Forro acústico com amortecedor (drywall ou mineral): absorção sonora, controle de reverberação e menos ruído entre andares. Projeto e instalação.',
        'h1': 'Controle a reverberação com <em>Forro Acústico com Amortecedor</em>',
        'lead': 'Este tipo de forro proporciona grande absorção sonora, controla a reverberação e atenua a transmissão de ruídos entre ambientes, garantindo maior privacidade e conforto acústico.',
        'checks': ['Grande absorção sonora no ambiente interno.', 'Reduz a transmissão de ruídos entre um ambiente e outro.', 'Diversos modelos de forro, como drywall e mineral.'],
        'img': 'forro-acustico2', 'img_alt': 'Sistema de forro acústico com amortecedor instalado',
        'problema': 'O eco e a falta de privacidade sonora são um problema no seu ambiente?',
        'solucao': 'Um forro acústico com amortecedor é a solução ideal. Ele controla a reverberação sonora, melhorando a inteligibilidade do som, e proporciona maior privacidade, pois a transmissão de ruídos entre um ambiente e outro é bastante atenuada.',
        'aplicacoes_titulo': 'Ideal para ambientes com alta exigência acústica',
        'aplicacoes': [('building-2', 'Escritórios e Corporativo'), ('presentation', 'Auditórios e Teatros'), ('utensils-crossed', 'Restaurantes e Bares'), ('graduation-cap', 'Salas de Aula')],
        'specs_titulo': 'Modelos e especificações',
        'specs': [('Sistema', 'Forro suspenso com amortecedores para desvinculação da laje.'), ('Modelos', 'Trabalhamos com diversos modelos, entre eles drywall e mineral.'), ('Funcionalidade', 'Absorção sonora e controle da reverberação interna.'), ('Benefício adicional', 'Atenua a transmissão de ruídos aéreos e de impacto entre andares.')],
    },
    {
        'slug': 'janela-acustica', 'nome': 'Janela Acústica', 'card': 'janelas-acusticas',
        'titulo': 'Janela Acústica: até 30 dB de isolamento | Solucionne',
        'descricao': 'Janelas acústicas em alumínio com vidro laminado: linhas Basic, Confort e Advanced, isolamento de até 30 dB. Instalação sobreposta ou embutida.',
        'h1': 'O fim do barulho: conforto e silêncio com as <em>Janelas Acústicas</em> Solucionne',
        'lead': 'Tecnologia de ponta para isolar ruídos externos e garantir sua tranquilidade, seja em casa ou no trabalho.',
        'checks': ['Paz e sossego para sua família.', 'Foco e produtividade no seu trabalho.', 'Valorização do seu imóvel.'],
        'img': 'janelas-acusticas', 'img_alt': 'Janela acústica de correr instalada em quarto',
        'problema': 'O barulho da cidade está invadindo seu espaço?',
        'solucao': 'Nossas esquadrias são a solução definitiva. Fabricadas em alumínio com vedação superior e vidros laminados insulados, elas garantem a vedação ideal para edifícios residenciais, comerciais ou industriais.',
        'extra': 'janela',
    },
    {
        'slug': 'jateamento-termo-acustico', 'nome': 'Jateamento Termo-Acústico', 'card': 'jateamento-termo-acustico',
        'titulo': 'Jateamento Termoacústico: menos eco e calor | Solucionne',
        'descricao': 'Jateamento termoacústico com fibras minerais resistentes ao fogo, laudo IPT. Reduz eco e calor em galpões, igrejas, auditórios e restaurantes.',
        'h1': 'Conforto e eficiência com <em>Jateamento Termoacústico</em>',
        'lead': 'Aplicação de fibras resistentes ao fogo para reduzir o tempo de reverberação (eco) e o calor, garantindo um ambiente mais agradável e produtivo.',
        'checks': ['Excelente material com performance comprovada por laudo IPT.', 'Fibras autoextinguíveis, resistentes ao fogo.', 'Reduz o eco e melhora o conforto térmico do ambiente.'],
        'img': 'jateamento-termo-acustico2', 'img_alt': 'Teto com aplicação de jateamento termoacústico Solufibra',
        'problema': 'O excesso de eco e calor compromete seu ambiente?',
        'solucao': 'O Jateamento Termoacústico Solufibra é a solução ideal. Aplicado diretamente na superfície, cria uma camada monolítica que absorve o som e isola o calor, transformando o conforto do seu espaço.',
        'aplicacoes_titulo': 'Ideal para grandes áreas e espaços com eco',
        'aplicacoes': [('building-2', 'Indústrias e Galpões'), ('church', 'Igrejas e Templos'), ('presentation', 'Auditórios e Teatros'), ('utensils-crossed', 'Restaurantes e Bares')],
        'specs_titulo': 'Especificações técnicas',
        'specs': [('Composto', 'Fibras minerais resistentes ao fogo (Solufibra).'), ('Espessura padrão', '25 mm.'), ('Densidade', '63 kg/m³.'), ('Segurança', 'Material autoextinguível, não propaga chamas.')],
    },
    {
        'slug': 'paineis-acusticos', 'nome': 'Painéis Acústicos', 'card': 'paineis-de-absorcao-sonora',
        'titulo': 'Painéis Acústicos Personalizados em MDF e Madeira | Solucionne',
        'descricao': 'Painéis acústicos em MDF ou madeira, personalizados com padrões, desenhos e logos. Tratamento acústico com design para auditórios e escritórios.',
        'h1': 'Tratamento acústico com <em>design sofisticado</em>: Painéis Acústicos',
        'lead': 'Nossos painéis acústicos em MDF ou madeira possuem acabamento de alta qualidade e podem ser personalizados com diferentes padrões, desenhos e logos para se adequarem perfeitamente ao seu projeto.',
        'checks': ['Acabamento em laminado melamínico ou madeira.', 'Soluções acústicas e/ou decorativas.', 'Totalmente personalizados para o seu ambiente.'],
        'img': 'painel-acustico2', 'img_alt': 'Auditório com painéis acústicos personalizados nas paredes',
        'problema': 'Precisa de um ambiente com acústica perfeita e visual impecável?',
        'solucao': 'Os painéis acústicos da Solucionne têm como finalidade o tratamento de ambientes internos com qualidade e um visual sofisticado. Visamos soluções que se adequem a ambientes com diferentes necessidades, conforme o projeto arquitetônico.',
        'aplicacoes_titulo': 'Soluções versáteis para ambientes exigentes',
        'aplicacoes': [('presentation', 'Auditórios e Teatros'), ('briefcase', 'Escritórios e Empresas'), ('users', 'Salas de Reunião'), ('film', 'Home Cinemas')],
        'specs_titulo': 'Especificações técnicas',
        'specs': [('Material', 'Produzidos em MDF ou madeira.'), ('Acabamento', 'Extensa variedade em laminado melamínico ou madeira.'), ('Design', 'Diferentes padrões, desenhos e logos personalizados.'), ('Projeto', 'Execução conforme o projeto arquitetônico do cliente.')],
    },
    {
        'slug': 'parede-acustica', 'nome': 'Parede Acústica', 'card': 'parede-acustica-com-amortecedor',
        'titulo': 'Parede Acústica com Amortecedor: isolamento entre ambientes | Solucionne',
        'descricao': 'Parede acústica com amortecedor e placa dupla de gesso acartonado: isolamento entre salas, estúdios e residências geminadas. Projeto e execução.',
        'h1': 'Isolamento acústico de alta performance para <em>paredes e divisórias</em>',
        'lead': 'Com barreiras verticais e construção adequada, nosso sistema com amortecedores isola o som até o nível desejado, ideal para diversos tipos de construção, como paredes duplas ou de cavidade.',
        'checks': ['Vários designs para barreiras e divisórias verticais.', 'Solução eficiente para paredes homogêneas, porosas ou duplas.', 'Construção de parede de cavidade para máximo isolamento.'],
        'img': 'parede-acustica2', 'img_alt': 'Corte de parede com amortecedor, montante e placa dupla de gesso acartonado',
        'problema': 'O ruído entre ambientes atrapalha sua privacidade e concentração?',
        'solucao': 'O isolamento de parede com barreiras verticais e divisórias é a solução. Com uma construção adequada, utilizando amortecedores e sistemas como a parede de cavidade, é possível isolar o som até o nível desejado, garantindo conforto e tranquilidade.',
        'aplicacoes_titulo': 'Perfeito para ambientes que exigem silêncio',
        'aplicacoes': [('mic', 'Estúdios de Gravação'), ('house', 'Residências (Geminadas)'), ('briefcase', 'Escritórios Corporativos'), ('film', 'Home Cinemas')],
        'specs_titulo': 'Estrutura do sistema',
        'specs': [('1. Base', 'Parede existente.'), ('2. Isolamento', 'Amortecedor acústico para desvincular as estruturas.'), ('3. Estrutura', 'Montante metálico (M48, M70 ou M90).'), ('4. Acabamento', 'Placa dupla de gesso acartonado.')],
    },
    {
        'slug': 'pisos-acusticos', 'nome': 'Pisos Acústicos', 'card': 'pisos-silenciadores',
        'titulo': 'Piso Acústico (Contrapiso Flutuante) contra ruído de impacto | Solucionne',
        'descricao': 'Piso elevado com amortecedor (contrapiso flutuante): reduz ruído de passos, queda de objetos e móveis entre andares. Para prédios, hospitais e escolas.',
        'h1': 'Isolamento superior contra ruídos de impacto com <em>Piso Elevado</em>',
        'lead': 'Também conhecido como contrapiso flutuante, nosso sistema é fundamental para garantir o isolamento acústico em edifícios, minimizando a transmissão de ruídos causados por passos, queda de objetos e arrastar de móveis.',
        'checks': ['Reduz drasticamente o ruído de impacto entre andares.', 'Essencial para edifícios residenciais e corporativos.', 'Instalação especializada que garante a eficácia do isolamento.'],
        'img': 'piso-acustico2', 'img_alt': 'Camadas de um sistema de piso elevado com amortecedor',
        'problema': 'O barulho do vizinho de cima é um problema?',
        'solucao': 'O piso silenciador é um elemento fundamental para garantir o conforto acústico. Nosso sistema de contrapiso flutuante é projetado para minimizar a transmissão de ruídos, exigindo uma instalação cuidadosa e materiais resilientes para evitar pontes acústicas e garantir a eficácia.',
        'aplicacoes_titulo': 'Essencial para a construção civil moderna',
        'aplicacoes': [('building', 'Edifícios Residenciais'), ('briefcase', 'Prédios Comerciais'), ('hospital', 'Hospitais e Clínicas'), ('graduation-cap', 'Escolas e Universidades')],
        'specs_titulo': 'Especificações técnicas',
        'specs': [('Sistema', 'Contrapiso flutuante com amortecedores resilientes.'), ('Aplicação', 'Diretamente sobre a laje, antes do acabamento final.'), ('Eficiência', 'Garantida por ensaios em laboratório e normas técnicas.'), ('Instalação', 'Requer cuidados específicos para evitar pontes acústicas.')],
    },
    {
        'slug': 'portas-acusticas', 'nome': 'Portas Acústicas', 'card': 'portas-acusticas',
        'titulo': 'Portas Acústicas em madeira, aço ou vidro | Solucionne',
        'descricao': 'Portas acústicas em madeira maciça, aço ou vidro com vedação de frestas em todo o perímetro. Para estúdios, escritórios, residências e hotéis.',
        'h1': 'Silêncio e segurança com as <em>Portas Acústicas</em> da Solucionne',
        'lead': 'Garanta um ambiente mais silencioso e confortável. Nossas portas bloqueiam ruídos externos e são a melhor opção para residências e organizações.',
        'checks': ['Sistema completo de vedação de frestas.', 'Modelos em madeira maciça, aço ou vidro.', 'Instalação profissional realizada por nossa equipe.'],
        'img': 'porta-acustica2', 'img_alt': 'Porta acústica de madeira instalada',
        'problema': 'O barulho externo atrapalha sua paz e produtividade?',
        'solucao': 'Para reduzir o desconforto sonoro que prevalece nas regiões urbanas, fabricamos portas que criam uma barreira eficaz contra ruídos indesejados.',
        'aplicacoes_titulo': 'Ideal para ambientes que exigem silêncio',
        'aplicacoes': [('film', 'Estúdios e Home Cinemas'), ('briefcase', 'Escritórios e Reuniões'), ('house', 'Residências Urbanas'), ('hotel', 'Quartos de Hotel')],
        'specs_titulo': 'Especificações técnicas',
        'specs': [('Materiais', 'Madeira maciça, aço ou vidro laminado insulado.'), ('Vedação', 'Sistema de vedação de frestas em todo o perímetro.'), ('Estrutura', 'Entregues com toda a estrutura necessária para instalação.'), ('Instalação', 'Realizada por nossa equipe técnica especializada.')],
    },
    {
        'slug': 'visores-acusticos', 'nome': 'Visores Acústicos', 'card': 'visores-acusticos',
        'titulo': 'Visores Acústicos para estúdios e salas técnicas | Solucionne',
        'descricao': 'Visores acústicos com vidro fixo laminado, duplo ou triplo e câmara de ar desidratada: visão entre ambientes sem passagem de som. Sob medida.',
        'h1': 'Comunicação visual sem interferência com <em>Visores Acústicos</em>',
        'lead': 'Nossas esquadrias com folhas de vidro fixo garantem a visualização entre ambientes, bloqueando a passagem de som.',
        'checks': ['Visibilidade total sem ruídos.', 'Perfeito para estúdios, salas de reunião e locais técnicos.', 'Fabricação sob medida para seu projeto.'],
        'img': 'visores-acustico2', 'img_alt': 'Visor acústico instalado entre duas salas',
        'problema': 'Precisa ver o que acontece em outro ambiente, mas sem o barulho?',
        'solucao': 'Os visores acústicos possibilitam a comunicação visual clara entre espaços, sendo essenciais em locais que necessitam de visualização do andamento de serviços ou procedimentos sem qualquer interferência sonora.',
        'aplicacoes_titulo': 'Perfeito para comunicação visual crítica',
        'aplicacoes': [('mic', 'Estúdios de Gravação'), ('users', 'Salas de Reunião'), ('sliders-horizontal', 'Cabines de Controle'), ('hard-drive', 'Locais Técnicos')],
        'specs_titulo': 'Especificações técnicas',
        'specs': [('Estrutura', 'Esquadrias robustas em aço ou madeira.'), ('Vidro', 'Folhas de vidro fixo (laminado, duplo ou triplo).'), ('Isolamento', 'Câmara de ar interna desidratada para evitar embaçamento.'), ('Finalidade', 'Permitir comunicação visual sem interferência de ruídos.')],
    },
]

SERVICOS = [
    ('bar-chart-4', 'Análise de Ruídos', 'Diagnóstico preciso das fontes de ruído e seus níveis de impacto.'),
    ('map', 'Mapeamento Acústico', 'Visualização detalhada da distribuição sonora no ambiente.'),
    ('drafting-compass', 'Projeto Acústico', 'Desenvolvimento de soluções customizadas para controle de ruído.'),
    ('speaker', 'Projeto Eletroacústico', 'Planejamento de sistemas de som para máxima inteligibilidade.'),
    ('hard-hat', 'Execução de Obras', 'Implementação de projetos com equipe e materiais especializados.'),
    ('file-check-2', 'Laudos Técnicos', 'Emissão de laudos em conformidade com as normas ABNT.'),
]

AMBIENTES = [
    ('imagem-destaque2', 'Residências', 'Ambiente residencial com tratamento acústico',
     'Soluções que garantem conforto e privacidade: do isolamento de ruídos externos a home cinemas com acústica perfeita.'),
    ('imagem-destaque3', 'Comércios', 'Salão comercial com tratamento acústico',
     'Lojas, restaurantes e escritórios com menos reverberação, melhor experiência do cliente e mais produtividade.'),
    ('projeto', 'Indústrias', 'Projeto acústico sendo desenhado em planta',
     'Projetos focados em segurança e conformidade com as normas de ruído: enclausuramento de máquinas, barreiras acústicas e proteção auditiva.'),
]

CLIENTES = [('audi', 'Audi'), ('banco-do-brasil', 'Banco do Brasil'), ('correios', 'Correios'), ('inter', 'Inter'), ('oi', 'Oi'), ('sebrae', 'Sebrae')]
ASSOCIACOES = [('abnt', 'ABNT – Associação Brasileira de Normas Técnicas'), ('pro-acustica', 'ProAcústica – empresa associada'), ('sobrac', 'SOBRAC – Sociedade Brasileira de Acústica')]

# Perguntas frequentes: só respostas com informação já publicada pela empresa
FAQ = [
    ('A Solucionne atende residências, comércios e indústrias?',
     'Sim. Fazemos soluções sob medida para ambientes residenciais, comerciais e industriais: do isolamento de ruídos externos em casa ao controle de ruído em fábricas, conforme as normas técnicas.'),
    ('Quais serviços de acústica vocês oferecem?',
     'Análise de ruídos, mapeamento acústico, projeto acústico, projeto eletroacústico, execução de obras e emissão de laudos técnicos em conformidade com as normas ABNT. Da consultoria ao laudo final.'),
    ('Quais produtos acústicos a Solucionne trabalha?',
     'Difusores, espumas, forro acústico com amortecedor, janelas acústicas, jateamento termoacústico, painéis acústicos, parede acústica com amortecedor, pisos acústicos (contrapiso flutuante), portas acústicas e visores acústicos.'),
    ('Como peço um orçamento?',
     f"Pelo formulário desta página, pelo WhatsApp {E['telefone']} ou pelo e-mail {E['email']}. Conte o tipo de ambiente e o problema de ruído que você quer resolver."),
    ('Onde fica a Solucionne?',
     f"Em {ENDERECO}."),
]

# =====================================================================
# Utilitários
# =====================================================================
esc = html.escape


def icone(nome, classe='icon'):
    caminho = os.path.join(ICONES, nome + '.svg')
    with open(caminho) as f:
        preenchido = 'data-preenchido' in f.read()
    extra = ' icon--fill' if preenchido else ''
    return f'<svg class="{classe}{extra}" aria-hidden="true"><use href="#i-{nome}"/></svg>'


ICONES_USADOS = set()


def ic(nome, classe='icon'):
    ICONES_USADOS.add(nome)
    return icone(nome, classe)


def sprite(nomes):
    simbolos = []
    for nome in sorted(nomes):
        with open(os.path.join(ICONES, nome + '.svg')) as f:
            svg = f.read()
        corpo = re.search(r'<svg[^>]*>(.*)</svg>', svg, re.S).group(1)
        corpo = re.sub(r'<!--.*?-->', '', corpo, flags=re.S)
        corpo = re.sub(r'\s+', ' ', corpo).strip()
        simbolos.append(f'<symbol id="i-{nome}" viewBox="0 0 24 24">{corpo}</symbol>')
    return '<svg class="sprite" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">' + ''.join(simbolos) + '</svg>'


def img(base, alt, sizes, classe='', eager=False, w_attr=None):
    """<img> com srcset das larguras geradas por otimizar_imagens.py."""
    info = IMAGENS[base]
    larguras = info['larguras']
    srcset = ', '.join(f'/assets/img/{base}-{w}.webp {w}w' for w in larguras)
    w = larguras[-1]
    h = round(w * info['proporcao'])
    carregamento = 'fetchpriority="high"' if eager else 'loading="lazy"'
    cls = f' class="{classe}"' if classe else ''
    return (f'<img src="/assets/img/{base}-{larguras[0]}.webp" srcset="{srcset}" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{esc(alt)}" {carregamento} decoding="async"{cls}>')


def preload(base, sizes):
    info = IMAGENS[base]
    srcset = ', '.join(f'/assets/img/{base}-{w}.webp {w}w' for w in info['larguras'])
    return f'<link rel="preload" as="image" type="image/webp" imagesrcset="{srcset}" imagesizes="{sizes}" fetchpriority="high">'


def jsonld(dados):
    return '<script type="application/ld+json">' + json.dumps(dados, ensure_ascii=False, separators=(',', ':')) + '</script>'


NEGOCIO_ID = f'{URL}/#negocio'

# =====================================================================
# Blocos comuns
# =====================================================================

def head(*, titulo, descricao, caminho, tipo_pagina, indexar=True, schema=None, extra=''):
    canonical = URL + caminho
    robots = 'index, follow, max-image-preview:large' if indexar else 'noindex, follow'
    v = VERSAO_ICONE
    return f'''<!DOCTYPE html>
<html lang="pt-BR" data-pagina="{tipo_pagina}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- Gerado por ferramentas/gerar_paginas.py — não edite à mão -->
  <script src="/assets/js/rastreamento.js"></script>
  <title>{esc(titulo)}</title>
  <meta name="description" content="{esc(descricao)}">
  <meta name="robots" content="{robots}">
  <meta name="theme-color" content="#0E0E0F">
  <link rel="canonical" href="{canonical}">
  <meta name="geo.region" content="BR-{E['uf']}">
  <meta name="geo.placename" content="{E['cidade']}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="pt_BR">
  <meta property="og:site_name" content="{E['nome_completo']}">
  <meta property="og:title" content="{esc(titulo)}">
  <meta property="og:description" content="{esc(descricao)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{URL}/assets/img/og-image-2.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="preload" href="/assets/fonts/inter-latin-var.woff2" as="font" type="font/woff2" crossorigin>
  {extra}
  <link rel="stylesheet" href="/assets/css/styles.css">
  <script defer src="/assets/js/main.js"></script>
  <link rel="icon" type="image/png" href="/assets/favicon/favicon-96x96.png?v={v}" sizes="96x96">
  <link rel="shortcut icon" href="/assets/favicon/favicon.ico?v={v}">
  <link rel="apple-touch-icon" sizes="180x180" href="/assets/favicon/apple-touch-icon.png?v={v}">
  <link rel="manifest" href="/assets/favicon/site.webmanifest?v={v}">
  {jsonld(schema) if schema else ''}
</head>'''


def nav(ativo=''):
    atual = ' aria-current="page"'
    itens_produtos = ''.join(
        f'<a href="/{p["slug"]}"{atual if p["slug"] == ativo else ""}>{p["nome"]}</a>'
        for p in PRODUTOS)
    return f'''
  <header class="nav">
    <div class="wrap nav__inner">
      <a class="nav__logo" href="/" aria-label="{E['nome']} – página inicial"><img src="/assets/img/logo.png" width="246" height="44" alt="{E['nome_completo']}"></a>
      <nav aria-label="Principal">
        <ul class="nav__menu" id="menu">
          <li><a href="/#sobre">Sobre</a></li>
          <li><a href="/#solucoes">Soluções</a></li>
          <li class="nav__sub">
            <button type="button" aria-expanded="false" aria-controls="menu-produtos">Produtos {ic('chevron-down')}</button>
            <div class="nav__panel" id="menu-produtos">{itens_produtos}</div>
          </li>
          <li><a href="/#clientes">Clientes</a></li>
          <li><a href="/#contato">Contato</a></li>
          <li class="nav__menu-cta"><a class="btn btn--red btn--block" href="#contato">Solicitar orçamento</a></li>
        </ul>
      </nav>
      <div class="nav__cta">
        <a class="btn btn--red btn--sm" href="#contato">Solicitar orçamento</a>
        <button type="button" class="nav__toggle" aria-label="Abrir menu" aria-expanded="false" aria-controls="menu">{ic('menu', 'icon icon--abrir')}{ic('x', 'icon icon--fechar')}</button>
      </div>
    </div>
  </header>'''


def social():
    return '<div class="social">' + ''.join(
        f'<a href="{url}" target="_blank" rel="noopener" aria-label="{rede} da {E["nome"]}">{ic(icone_)}</a>'
        for rede, icone_, url in E['redes']) + '</div>'


def footer():
    produtos = ''.join(f'<li><a href="/{p["slug"]}">{p["nome"]}</a></li>' for p in PRODUTOS)
    return f'''
  <footer class="footer">
    <div class="wrap">
      <div class="footer__grid">
        <div>
          <a class="footer__logo" href="/"><img src="/assets/img/logo.png" width="246" height="44" alt="{E['nome_completo']}" loading="lazy"></a>
          <p>{E['descricao_curta']}</p>
          {social()}
        </div>
        <div>
          <h2>Navegação</h2>
          <ul>
            <li><a href="/#sobre">Sobre nós</a></li>
            <li><a href="/#solucoes">Soluções</a></li>
            <li><a href="/#produtos">Produtos</a></li>
            <li><a href="/#clientes">Clientes</a></li>
            <li><a href="/#duvidas">Dúvidas frequentes</a></li>
            <li><a href="/#contato">Contato</a></li>
          </ul>
        </div>
        <div>
          <h2>Produtos</h2>
          <ul>{produtos}</ul>
        </div>
        <div>
          <h2>Contato</h2>
          <ul>
            <li><a href="{ROTA}" target="_blank" rel="noopener"><address>{E['rua']} – {E['bairro']}<br>{E['cidade']} – {E['uf']}, {E['cep']}</address></a></li>
            <li><a href="tel:{E['telefone_link']}">{E['telefone']}</a></li>
            <li><a href="mailto:{E['email']}">{E['email']}</a></li>
            <li><a href="{whats('Olá! Gostaria de mais informações sobre as soluções acústicas.')}" data-interesse="Contato geral">WhatsApp</a></li>
          </ul>
        </div>
      </div>
      <div class="footer__base">
        <p>&copy; <span id="ano">{date.today().year}</span> {E['nome_completo']}. Todos os direitos reservados.</p>
        <p class="footer__legal"><a href="/politica-de-privacidade">Política de privacidade</a><button type="button" data-abrir-cookies>Preferências de cookies</button></p>
      </div>
    </div>
  </footer>'''


def float_whats(texto='Olá! Gostaria de mais informações sobre as soluções acústicas.', interesse='Contato geral'):
    return f'''
  <a class="float-whats" href="{whats(texto)}" target="_blank" rel="noopener" data-interesse="{esc(interesse)}" aria-label="Conversar no WhatsApp">{ic('whatsapp')}</a>'''


def popup():
    return f'''
  <dialog class="lead" id="lead-whats" aria-labelledby="lead-titulo">
    <button type="button" class="lead__close" data-fechar aria-label="Fechar">&times;</button>
    <span class="lead__icon">{ic('whatsapp')}</span>
    <h3 id="lead-titulo">Vamos conversar no WhatsApp</h3>
    <p class="lead__sub" id="lead-interesse">Informe seu nome e telefone para continuar.</p>
    <form id="lead-form" novalidate>
      <label class="field">
        <span>Nome</span>
        <input type="text" name="nome" autocomplete="name" required>
      </label>
      <label class="field">
        <span>Telefone / WhatsApp</span>
        <input type="tel" name="telefone" autocomplete="tel" inputmode="tel" placeholder="(31) 90000-0000" required>
      </label>
      <p class="hp" aria-hidden="true"><label>Não preencha: <input name="empresa" tabindex="-1" autocomplete="off"></label></p>
      <p class="lead__erro" id="lead-erro" role="alert"></p>
      <button type="submit" class="btn btn--whats btn--block">{ic('whatsapp')}Continuar no WhatsApp</button>
      <p class="lead__nota">Seus dados ficam só com a {E['nome']}. <a href="/politica-de-privacidade">Política de Privacidade</a></p>
    </form>
  </dialog>'''


def contato(interesse='', titulo='Vamos começar seu projeto?', texto_whats='Olá! Gostaria de mais informações sobre as soluções acústicas.'):
    return f'''
    <section class="section section--alt" id="contato">
      <div class="wrap contact">
        <div class="contact__info reveal">
          <p class="kicker">Contato</p>
          <h2>{titulo}</h2>
          <p>Fale com nossos consultores pelo formulário ou direto pelos nossos canais. Respondemos com a solução adequada ao seu ambiente.</p>
          <ul class="contact__lista">
            <li><span class="pilar__icone">{ic('whatsapp')}</span><a href="{whats(texto_whats)}" target="_blank" rel="noopener" data-interesse="{esc(interesse or 'Contato geral')}"><small>WhatsApp</small>{E['telefone']}</a></li>
            <li><span class="pilar__icone">{ic('phone')}</span><a href="tel:{E['telefone_link']}"><small>Telefone</small>{E['telefone']}</a></li>
            <li><span class="pilar__icone">{ic('mail')}</span><a href="mailto:{E['email']}"><small>E-mail</small>{E['email']}</a></li>
            <li><span class="pilar__icone">{ic('map-pin')}</span><a href="{ROTA}" target="_blank" rel="noopener"><small>Endereço · traçar rota</small>{ENDERECO}</a></li>
          </ul>
          <div class="contact__acoes">
            <a class="btn btn--whats" href="{whats(texto_whats)}" target="_blank" rel="noopener" data-interesse="{esc(interesse or 'Contato geral')}">{ic('whatsapp')}Chamar no WhatsApp</a>
          </div>
        </div>
        <div class="form-card reveal">
          <h3>Solicite um orçamento</h3>
          <p>Conte sobre o ambiente e o problema de ruído. Retornamos o contato.</p>
          <form id="contato-form" name="orcamento" method="POST" action="/api/orcamento">
            <p class="hp" aria-hidden="true"><label>Não preencha: <input name="empresa" tabindex="-1" autocomplete="off"></label></p>
            <label class="field">
              <span>Nome</span>
              <input type="text" name="nome" autocomplete="name" required>
            </label>
            <div class="field-row">
              <label class="field">
                <span>E-mail</span>
                <input type="email" name="email" autocomplete="email" required>
              </label>
              <label class="field">
                <span>Telefone</span>
                <input type="tel" name="telefone" autocomplete="tel" inputmode="tel" placeholder="(31) 90000-0000" required>
              </label>
            </div>
            <label class="field">
              <span>Mensagem</span>
              <textarea name="mensagem" rows="5" placeholder="Conte-nos sobre seu projeto" required></textarea>
            </label>
            <input type="hidden" name="interesse" value="{esc(interesse)}">
            <input type="hidden" name="utm_source" id="utm_source">
            <input type="hidden" name="utm_medium" id="utm_medium">
            <input type="hidden" name="utm_campaign" id="utm_campaign">
            <input type="hidden" name="utm_content" id="utm_content">
            <input type="hidden" name="utm_term" id="utm_term">
            <button type="submit" class="btn btn--red btn--block">Enviar mensagem</button>
            <p class="form-status" id="form-status" role="status" aria-live="polite"></p>
            <p class="form-legal">Ao enviar, você concorda com a <a href="/politica-de-privacidade">Política de Privacidade</a>.</p>
          </form>
        </div>
      </div>
    </section>'''


def pagina(cabeca, corpo, *, body_attrs=''):
    """Monta a página: o sprite entra por último na lista de ícones, já com todos os usados."""
    global ICONES_USADOS
    usados = set(ICONES_USADOS)
    ICONES_USADOS = set()
    return f'''{cabeca}
<body{body_attrs}>
  <a class="skip-link" href="#conteudo">Pular para o conteúdo</a>
  {sprite(usados)}
{corpo}
</body>
</html>
'''


def eq(n=36):
    # Barras do equalizador com alturas e atrasos variados (decorativo)
    barras = []
    for i in range(n):
        alt = 25 + ((i * 37) % 70)
        atraso = -((i * 0.13) % 1.4)
        barras.append(f'<span style="height:{alt}%;animation-delay:{atraso:.2f}s"></span>')
    return '<div class="eq" aria-hidden="true">' + ''.join(barras) + '</div>'


def negocio():
    return {
        '@type': 'HomeAndConstructionBusiness',
        '@id': NEGOCIO_ID,
        'name': E['nome_completo'],
        'alternateName': E['nome'],
        'description': E['descricao_curta'],
        'url': URL + '/',
        'image': f'{URL}/assets/img/og-image-2.jpg',
        'logo': f'{URL}/assets/favicon/web-app-manifest-512x512.png',
        'telephone': '+55-31-3442-1713',
        'email': E['email'],
        'address': {'@type': 'PostalAddress', 'streetAddress': E['rua'], 'addressLocality': E['cidade'],
                    'addressRegion': E['uf'], 'postalCode': E['cep'], 'addressCountry': 'BR'},
        'areaServed': {'@type': 'Country', 'name': 'Brasil'},
        'sameAs': [url for _, _, url in E['redes']],
        'hasOfferCatalog': {'@type': 'OfferCatalog', 'name': 'Produtos e serviços acústicos', 'itemListElement': [
            {'@type': 'Offer', 'itemOffered': {'@type': 'Service', 'name': n}} for _, n, _ in SERVICOS
        ] + [
            {'@type': 'Offer', 'itemOffered': {'@type': 'Product', 'name': p['nome'], 'url': f"{URL}/{p['slug']}"}} for p in PRODUTOS
        ]},
    }


# =====================================================================
# Página inicial
# =====================================================================

def pagina_inicial():
    sizes_hero = '100vw'
    schema = {'@context': 'https://schema.org', '@graph': [
        negocio(),
        {'@type': 'WebSite', '@id': f'{URL}/#site', 'url': URL + '/', 'name': E['nome_completo'], 'inLanguage': 'pt-BR',
         'publisher': {'@id': NEGOCIO_ID}},
        {'@type': 'FAQPage', '@id': f'{URL}/#faq', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': r}} for q, r in FAQ]},
    ]}
    cabeca = head(
        titulo='Isolamento Acústico – Projetos e Obras em todo o Brasil | Solucionne',
        descricao='Isolamento e tratamento acústico em todo o Brasil: projeto, laudos ABNT e obra. Janelas, portas, forros, paredes e pisos acústicos. Peça seu orçamento.',
        caminho='/', tipo_pagina='inicio', schema=schema, extra=preload('imagem-destaque1', sizes_hero))

    servicos = ''.join(f'''
          <article class="service reveal">
            <span class="service__num">{i:02d}</span>
            {ic(icone_)}
            <h3>{t}</h3>
            <p>{d}</p>
          </article>''' for i, (icone_, t, d) in enumerate(SERVICOS, 1))

    ambientes = ''.join(f'''
          <article class="ambiente reveal">
            <div class="ambiente__img">{img(base, alt, '(max-width: 900px) 100vw, 33vw')}</div>
            <div class="ambiente__txt"><h3>{t}</h3><p>{txt}</p></div>
          </article>''' for base, t, alt, txt in AMBIENTES)

    produtos = ''.join(f'''
          <article class="card reveal">
            <div class="card__img">{img(p['card'], p['nome'], '(max-width: 640px) 50vw, (max-width: 900px) 33vw, (max-width: 1080px) 25vw, 230px')}</div>
            <div class="card__body"><h3><a href="/{p['slug']}">{p['nome']}</a></h3><span class="card__seta">{ic('arrow-up-right')}</span></div>
          </article>''' for p in PRODUTOS)

    clientes = ''.join(f'<li><img src="/assets/img/clientes/logo-cliente-{c}.webp" width="216" height="60" alt="{n}" loading="lazy"></li>' for c, n in CLIENTES)
    associacoes = ''.join(
        '<img src="/assets/img/associacoes/{0}.webp" width="{1}" height="{2}" alt="{3}" loading="lazy">'.format(
            a, *Image.open(os.path.join(PUBLIC, 'assets', 'img', 'associacoes', a + '.webp')).size, esc(n))
        for a, n in ASSOCIACOES)
    faq = ''.join(f'''
          <details class="faq__item">
            <summary>{esc(q)}</summary>
            <p>{esc(r)}</p>
          </details>''' for q, r in FAQ)

    texto_whats = 'Olá! Gostaria de mais informações sobre as soluções acústicas.'
    corpo = f'''{nav()}
  <main id="conteudo">
    <section class="hero">
      <div class="hero__media">{img('imagem-destaque1', 'Restaurante com painéis de madeira e tratamento acústico executado pela Solucionne', sizes_hero, eager=True)}</div>
      <div class="wrap">
        <div class="hero__content">
          <h1>
            <span class="hero__titulo">A solução ideal para seu <em>isolamento acústico.</em></span>
          </h1>
          <p class="hero__sub">Combinamos tradição, conhecimento técnico e inovação para transformar qualquer ambiente com desempenho acústico excepcional.</p>
          <div class="hero__acoes">
            <a class="btn btn--red" href="#contato">Solicitar orçamento {ic('arrow-right')}</a>
            <a class="btn btn--ghost" href="{whats(texto_whats)}" target="_blank" rel="noopener" data-interesse="Contato geral">{ic('whatsapp')}Falar no WhatsApp</a>
          </div>
          <div class="hero__selos">
            <div><strong>+24 anos</strong><span>no mercado de acústica</span></div>
            <div><strong>ABNT</strong><span>laudos conforme as normas</span></div>
            <div><strong>Top of Quality</strong><span>Gold Internacional</span></div>
          </div>
        </div>
      </div>
      {eq()}
    </section>

    <section class="selos" aria-label="Associações">
      <div class="wrap selos__inner">
        <p><strong>Associações do setor</strong>Fazemos parte de órgãos que regulamentam e promovem a qualidade no setor acústico.</p>
        <div class="selos__logos">{associacoes}</div>
      </div>
    </section>

    <section class="section" id="sobre">
      <div class="wrap sobre">
        <div class="sobre__texto reveal">
          <p class="kicker">Quem somos</p>
          <h2>Tradição e <span class="destaque-texto">experiência</span>.</h2>
          <p>Há mais de 24 anos no mercado, a Solucionne é referência nacional em soluções acústicas de alta performance. Nossa equipe é formada por arquitetos, engenheiros e técnicos especializados comprometidos com qualidade, inovação e conformidade normativa.</p>
        </div>
        <div class="pilares">
          <article class="pilar reveal"><span class="pilar__icone">{ic('target')}</span><div><h3>Missão</h3><p>Assegurar que nossos clientes tenham conforto, bem-estar, compromisso social e qualidade de vida, através do tratamento de seus ambientes com os produtos comercializados e os serviços prestados.</p></div></article>
          <article class="pilar reveal"><span class="pilar__icone">{ic('eye')}</span><div><h3>Visão</h3><p>Ser reconhecida por ousar em projetos com soluções modernas e adequadas ao conceito de acústica sustentável. Ser líder de mercado na customização de serviços acústicos em Minas Gerais.</p></div></article>
          <article class="pilar reveal"><span class="pilar__icone">{ic('gem')}</span><div><h3>Valores</h3><p>Verdade, profissionalismo, honestidade, companheirismo, colaboração e respeito pelas pessoas e pelo meio ambiente.</p></div></article>
        </div>
      </div>
    </section>

    <section class="section section--alt" id="solucoes">
      <div class="wrap">
        <div class="section__head reveal">
          <p class="kicker">Soluções completas</p>
          <h2>Da consultoria ao laudo final.</h2>
          <p>Soluções sob medida para ambientes residenciais, corporativos e industriais. Cada projeto é executado com precisão técnica e atenção aos detalhes.</p>
        </div>
        <div class="servicos">{servicos}
        </div>
      </div>
    </section>

    <section class="section" id="ambientes">
      <div class="wrap">
        <div class="section__head reveal">
          <p class="kicker">Ambientes atendidos</p>
          <h2>Atendemos todos os tipos de ambiente.</h2>
          <p>Seja para tornar sua casa mais silenciosa ou atender às exigências acústicas de grandes empreendimentos, temos a solução ideal para cada espaço.</p>
        </div>
        <div class="ambientes">{ambientes}
        </div>
      </div>
    </section>

    <section class="section section--light" id="produtos">
      <div class="wrap">
        <div class="section__head reveal">
          <p class="kicker">Produtos</p>
          <h2>Produtos de alta performance para controle de ruído.</h2>
          <p>Com tecnologia de ponta, desenvolvemos e aplicamos produtos certificados e eficientes que aliam estética, funcionalidade e performance.</p>
        </div>
        <div class="produtos">{produtos}
        </div>
      </div>
    </section>

    <section class="section" id="clientes">
      <div class="wrap">
        <div class="section__head section__head--center reveal">
          <p class="kicker">Clientes</p>
          <h2>Empresas que confiam na Solucionne.</h2>
          <p>Empresas líderes em seus segmentos confiam na Solucionne para soluções acústicas de alto padrão.</p>
        </div>
        <ul class="clientes reveal">{clientes}</ul>
      </div>
    </section>

    <section class="section section--red" id="premio">
      <div class="wrap premio">
        <figure class="reveal">
          {img('award-photo', 'Equipe Solucionne recebendo o prêmio Top of Quality Gold Internacional', '(max-width: 900px) 100vw, 40vw')}
          <figcaption>Reconhecimento “Top of Quality Gold Internacional”</figcaption>
        </figure>
        <div class="reveal">
          <p class="kicker">Premiação</p>
          <h2>Empresa reconhecida e premiada no comércio nacional.</h2>
          <p>A Solucionne tem a honra de ser reconhecida com o prêmio <strong>Top of Quality Gold Internacional</strong>, um selo que atesta nosso compromisso com a excelência, a inovação e a satisfação de nossos clientes em todo o território nacional.</p>
          <div class="premio__itens">
            <div><span>Excelência</span><strong>Qualidade comprovada</strong></div>
            <div><span>Inovação</span><strong>Soluções modernas</strong></div>
            <div><span>Confiança</span><strong>Reconhecimento nacional</strong></div>
          </div>
          <a class="btn btn--white" href="#contato">Fale com um consultor {ic('arrow-right')}</a>
        </div>
      </div>
    </section>

    <section class="section section--light" id="duvidas">
      <div class="wrap">
        <div class="section__head section__head--center reveal">
          <p class="kicker">Dúvidas frequentes</p>
          <h2>Perguntas frequentes</h2>
        </div>
        <div class="faq">{faq}
        </div>
      </div>
    </section>
{contato(texto_whats=texto_whats)}
  </main>
{footer()}
{float_whats()}
{popup()}'''
    return pagina(cabeca, corpo)


# =====================================================================
# Páginas de produto
# =====================================================================

def extra_janela(p):
    linhas = [
        ('Linha Basic', 'A essência da eficiência acústica. Solução acessível e eficaz.', 'janela-linha-basic', 'Vidro laminado de 8 mm', 'até 15 dB', 'R$ 2.480,00', False),
        ('Linha Confort', 'A escolha ideal para quem busca uma solução acessível e eficaz.', 'janela-linha-confort', 'Vidro laminado de 10 mm', 'até 20 dB', 'R$ 2.750,00', True),
        ('Linha Advanced', 'A excelência em isolamento. O ápice da tecnologia e desempenho.', 'janela-linha-advanced', 'Vidro quádruplo (6 mm + 8 mm)', 'até 30 dB', 'R$ 3.450,00', False),
    ]
    cards = ''.join(f'''
          <article class="linha reveal{' linha--destaque' if destaque else ''}">
            {'<span class="linha__selo">MAIS POPULAR</span>' if destaque else ''}
            <h3>{nome}</h3>
            <p>{desc}</p>
            {img(base, f'Corte do perfil da janela acústica {nome}', '(max-width: 900px) 90vw, 380px')}
            <dl>
              <div><dt>Composição</dt><dd>{comp}</dd></div>
              <div><dt>Isolamento</dt><dd>{iso}</dd></div>
            </dl>
            <div class="linha__preco"><small>A partir de</small><strong>{preco}</strong> <span>/m²</span></div>
            <a class="btn {'btn--red' if destaque else 'btn--ghost-dark'} btn--block" href="{whats(f'Olá! Gostaria de um orçamento de Janela Acústica – {nome}.')}" target="_blank" rel="noopener" data-interesse="Janela Acústica – {nome}">{ic('whatsapp')}Orçar a {nome}</a>
          </article>''' for nome, desc, base, comp, iso, preco, destaque in linhas)

    galeria = [
        ('janela-abertura-de-correr', 'Abertura de correr', 'Possui maior eficiência acústica devido à vedação superior.'),
        ('janela-abertura-de-giro', 'Abertura de giro', 'Alternativa para vãos e projetos que pedem abertura de giro.'),
        ('janela-instalacao-sobreposta', 'Instalação sobreposta', 'A esquadria é instalada sobre a janela existente, sem quebradeira.'),
        ('janela-instalacao-embutida', 'Instalação embutida', 'A janela atual é substituída pela nova esquadria acústica.'),
    ]
    figs = ''.join(f'''
          <figure class="reveal">{img(base, t, '(max-width: 640px) 100vw, 50vw')}<h3>{t}</h3><p>{d}</p></figure>''' for base, t, d in galeria)

    passos = [
        ('move-horizontal', '1. Meça a largura', 'Meça a largura interna do batente em 3 pontos (topo, meio e base) e anote o menor valor.'),
        ('move-vertical', '2. Meça a altura', 'Meça a altura interna do batente em 3 pontos (esquerda, centro e direita) e anote o menor valor.'),
        ('move-3d', '3. Meça a profundidade', 'Para instalação embutida, meça a profundidade do vão. Precisamos de no mínimo 7 cm.'),
    ]
    passos_html = ''.join(f'<article class="passo reveal">{ic(i)}<h3>{t}</h3><p>{d}</p></article>' for i, t, d in passos)

    return f'''
    <section class="section section--white janela-linhas" id="linhas">
      <div class="wrap">
        <div class="section__head section__head--center reveal">
          <p class="kicker">Linhas</p>
          <h2>Três linhas completas para sua necessidade.</h2>
        </div>
        <div class="linhas">{cards}
        </div>
        <p class="nota-precos">Valores de referência por m². O orçamento final depende das medidas, do tipo de abertura e da instalação.</p>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="section__head reveal">
          <p class="kicker">Design e instalação</p>
          <h2>Abertura e instalação flexíveis.</h2>
          <p>Oferecemos diferentes tipos de abertura e instalação para se adaptar perfeitamente ao seu projeto.</p>
        </div>
        <div class="galeria">{figs}
        </div>
      </div>
    </section>

    <section class="section section--light">
      <div class="wrap">
        <div class="section__head section__head--center reveal">
          <p class="kicker">Antes do orçamento</p>
          <h2>Como medir sua janela.</h2>
          <p>Siga estes 3 passos simples para um orçamento preciso.</p>
        </div>
        <div class="passos">{passos_html}</div>
      </div>
    </section>'''


def extra_espumas(p):
    return f'''
    <section class="section section--light">
      <div class="wrap">
        <div class="section__head reveal">
          <p class="kicker">Opções</p>
          <h2>Cores e espessuras.</h2>
        </div>
        <div class="opcoes">
          <div class="opcao reveal">
            <h3>Cores disponíveis</h3>
            <div class="cores">
              <span class="cor cor--chumbo"><i></i>CINZA CHUMBO</span>
              <span class="cor cor--gelo"><i></i>BRANCO GELO</span>
            </div>
            <p class="opcao__nota">Outras cores sob consulta.</p>
          </div>
          <div class="opcao reveal">
            <h3>Espessuras</h3>
            <ul class="chips"><li>25 mm</li><li>35 mm</li><li>50 mm</li><li>70 mm</li></ul>
          </div>
        </div>
      </div>
    </section>'''


def pagina_produto(p):
    caminho = '/' + p['slug']
    sizes_hero = '(max-width: 900px) 100vw, 50vw'
    schema = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'WebPage', '@id': URL + caminho, 'url': URL + caminho, 'name': p['titulo'], 'description': p['descricao'],
         'inLanguage': 'pt-BR', 'isPartOf': {'@id': f'{URL}/#site'}},
        {'@type': 'Service', 'name': p['nome'], 'description': p['descricao'], 'url': URL + caminho,
         'image': f"{URL}/assets/img/{p['img']}-{IMAGENS[p['img']]['larguras'][-1]}.webp",
         'provider': {'@type': 'HomeAndConstructionBusiness', '@id': NEGOCIO_ID, 'name': E['nome_completo'], 'url': URL + '/'},
         'areaServed': {'@type': 'Country', 'name': 'Brasil'}},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Início', 'item': URL + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Produtos', 'item': URL + '/#produtos'},
            {'@type': 'ListItem', 'position': 3, 'name': p['nome'], 'item': URL + caminho}]},
    ]}
    cabeca = head(titulo=p['titulo'], descricao=p['descricao'], caminho=caminho, tipo_pagina='produto',
                  schema=schema, extra=preload(p['img'], sizes_hero))
    texto_whats = f"Olá! Gostaria de um orçamento de {p['nome']}."
    checks = ''.join(f'<li>{ic("circle-check")}<span>{c}</span></li>' for c in p['checks'])

    aplicacoes = ''
    if p.get('aplicacoes'):
        tiles = ''.join(f'<article class="aplicacao reveal">{ic(i)}<h3>{t}</h3></article>' for i, t in p['aplicacoes'])
        aplicacoes = f'''
    <section class="section">
      <div class="wrap">
        <div class="section__head reveal">
          <p class="kicker">Aplicações</p>
          <h2>{p['aplicacoes_titulo']}.</h2>
        </div>
        <div class="aplicacoes">{tiles}</div>
      </div>
    </section>'''

    specs = ''
    if p.get('specs'):
        linhas = ''.join(f'<div><dt>{a}</dt><dd>{b}</dd></div>' for a, b in p['specs'])
        specs = f'''
    <section class="section section--white">
      <div class="wrap specs">
        <div class="section__head reveal">
          <p class="kicker">Ficha técnica</p>
          <h2>{p['specs_titulo']}.</h2>
          <p>Cada projeto é dimensionado para o seu ambiente. Fale com um consultor para definir a melhor configuração.</p>
        </div>
        <dl class="reveal">{linhas}</dl>
      </div>
    </section>'''

    extra = {'janela': extra_janela, 'espumas': extra_espumas}.get(p.get('extra'), lambda _: '')(p)
    outros = ''.join(f'<a href="/{o["slug"]}">{ic("arrow-up-right")}{o["nome"]}</a>' for o in PRODUTOS if o['slug'] != p['slug'])

    corpo = f'''{nav(p['slug'])}
  <main id="conteudo">
    <section class="hero hero--produto">
      <div class="wrap produto-hero">
        <div>
          <nav aria-label="Você está em"><ol class="migalhas"><li><a href="/">Início</a></li><li><a href="/#produtos">Produtos</a></li><li aria-current="page">{p['nome']}</li></ol></nav>
          <h1>{p['h1']}</h1>
          <p class="produto-hero__lead">{p['lead']}</p>
          <ul class="checks">{checks}</ul>
          <div class="hero__acoes">
            <a class="btn btn--red" href="#contato">Solicitar orçamento {ic('arrow-right')}</a>
            <a class="btn btn--ghost" href="{whats(texto_whats)}" target="_blank" rel="noopener" data-interesse="{esc(p['nome'])}">{ic('whatsapp')}Falar no WhatsApp</a>
          </div>
        </div>
        <div class="produto-hero__img">{img(p['img'], p['img_alt'], sizes_hero, eager=True)}</div>
      </div>
    </section>

    <section class="section section--light">
      <div class="wrap afirmacao reveal">
        <p class="kicker">O problema</p>
        <h2>{p['problema']}</h2>
        <p>{p['solucao']}</p>
      </div>
    </section>
{aplicacoes}{specs}{extra}
    <section class="section section--alt cta">
      <div class="wrap reveal">
        <p class="kicker">Outros produtos</p>
        <h2>Conheça outras soluções acústicas.</h2>
        <div class="cta__acoes outros">{outros}</div>
      </div>
    </section>
{contato(interesse=p['nome'], titulo=f"Vamos falar sobre {p['nome'].lower()}?", texto_whats=texto_whats)}
  </main>
{footer()}
{float_whats(texto_whats, p['nome'])}
{popup()}'''
    return pagina(cabeca, corpo)


# =====================================================================
# Links da bio, obrigado, 404, privacidade
# =====================================================================

def pagina_links():
    cabeca = head(titulo='Solucionne | Links', descricao='Canais oficiais da Solucionne: WhatsApp, site e redes sociais.',
                  caminho='/links', tipo_pagina='link_bio', indexar=False)
    utm = 'utm_source=instagram&utm_medium=social&utm_campaign=linkbio'

    def botao(texto, titulo, sub, conteudo, interesse, extra_cls=''):
        # Botão de WhatsApp: UTMs fixas no próprio link (o main.js as usa no registro do lead)
        attrs = (f' data-interesse="{esc(interesse)}" data-utm-source="instagram" data-utm-medium="social"'
                 f' data-utm-campaign="linkbio" data-utm-content="{conteudo}"')
        return (f'<a class="bio__link{extra_cls}" href="{whats(texto)}" target="_blank" rel="noopener"{attrs}>{ic("whatsapp")}'
                f'<span><strong>{titulo}</strong><small>{sub}</small></span>{ic("arrow-right")}</a>')

    links = [
        botao('Vim pelo Instagram e gostaria de um orçamento.', 'Fale no WhatsApp', 'Atendimento e orçamentos', 'whatsapp', 'Contato geral', ' bio__link--whats'),
        botao('Vim pelo Instagram e gostaria de um orçamento de Janela Acústica.', 'Orçamento de Janela Acústica', 'Linhas Basic, Confort e Advanced', 'whatsapp_janela', 'Janela Acústica'),
    ]
    paginas = [
        ('', 'globe', 'Visite nosso site', 'Produtos, soluções e obras', 'site'),
        ('janela-acustica', 'arrow-up-right', 'Janelas acústicas', 'Até 30 dB de isolamento', 'janela'),
        ('portas-acusticas', 'arrow-up-right', 'Portas acústicas', 'Madeira, aço ou vidro', 'portas'),
        ('', 'arrow-up-right', 'Todos os produtos', 'Forros, paredes, pisos, painéis e mais', 'produtos'),
    ]
    links_site = []
    for caminho, icone_, titulo, sub, conteudo in paginas:
        ancora = '#produtos' if conteudo == 'produtos' else ''
        href = f'/{caminho}?{utm}&utm_content={conteudo}{ancora}'
        links_site.append(f'<a class="bio__link" href="{href}">{ic(icone_)}<span><strong>{titulo}</strong><small>{sub}</small></span>{ic("arrow-right")}</a>')

    corpo = f'''
  <main id="conteudo" class="bio">
    <div class="bio__avatar"><img src="/assets/favicon/web-app-manifest-192x192.png" width="192" height="192" alt="Logo Solucionne"></div>
    <h1>{E['nome_completo']}</h1>
    <p class="bio__sub">{E['descricao_curta']}</p>
    {eq(28)}
    <div class="bio__links">
      {''.join(links)}
      <p class="bio__titulo">No site</p>
      {''.join(links_site)}
    </div>
    {social()}
    <p class="bio__rodape">&copy; {date.today().year} {E['nome_completo']} · <a href="/politica-de-privacidade">Privacidade</a></p>
  </main>
{popup()}'''
    return pagina(cabeca, corpo, body_attrs=' class="bio-page" data-utm-source="instagram" data-utm-medium="social" data-utm-campaign="linkbio"')


def pagina_simples(*, titulo, descricao, caminho, tipo, conteudo):
    cabeca = head(titulo=titulo, descricao=descricao, caminho=caminho, tipo_pagina=tipo, indexar=False)
    corpo = f'''
  <div class="simple">
    <header class="simple__top"><a href="/"><img src="/assets/img/logo.png" width="246" height="44" alt="{E['nome_completo']} – página inicial"></a></header>
{conteudo}
  </div>
{float_whats()}
{popup()}'''
    return pagina(cabeca, corpo)


def pagina_obrigado():
    return pagina_simples(titulo='Mensagem enviada | Solucionne', descricao='Recebemos sua mensagem.', caminho='/obrigado', tipo='obrigado', conteudo=f'''
    <main id="conteudo" class="aviso">
      <div>
        <p class="kicker">Mensagem enviada</p>
        <h1>Obrigado pelo contato!</h1>
        <p>Recebemos sua mensagem e um consultor da Solucionne vai retornar em breve. Se preferir, fale agora pelo WhatsApp.</p>
        <div class="cta__acoes">
          <a class="btn btn--whats" href="{whats('Olá! Acabei de enviar uma mensagem pelo site.')}" target="_blank" rel="noopener" data-interesse="Contato geral">{ic('whatsapp')}Chamar no WhatsApp</a>
          <a class="btn btn--ghost" href="/">Voltar ao site</a>
        </div>
      </div>
    </main>''')


def pagina_404():
    return pagina_simples(titulo='Página não encontrada | Solucionne', descricao='Página não encontrada.', caminho='/404', tipo='erro_404', conteudo=f'''
    <main id="conteudo" class="aviso">
      <div>
        <p class="kicker">Erro 404</p>
        <h1>Esta página ficou em silêncio.</h1>
        <p>O endereço pode ter mudado. Veja nossos produtos ou fale com a gente.</p>
        <div class="cta__acoes">
          <a class="btn btn--red" href="/">Ir para o início</a>
          <a class="btn btn--ghost" href="/#produtos">Ver produtos</a>
        </div>
      </div>
    </main>''')


def pagina_privacidade():
    return pagina_simples(titulo='Política de Privacidade | Solucionne', descricao='Como a Solucionne trata os dados pessoais de quem usa o site (LGPD).',
                          caminho='/politica-de-privacidade', tipo='privacidade', conteudo=f'''
    <main id="conteudo" class="legal">
      <p class="kicker">LGPD</p>
      <h1>Política de Privacidade</h1>
      <p class="legal__data">Última atualização: {date.today().strftime('%d/%m/%Y')}</p>

      <p>Esta política explica como a <strong>{E['nome_completo']}</strong> ({ENDERECO}) trata os dados pessoais de quem usa este site, de acordo com a Lei Geral de Proteção de Dados (Lei nº 13.709/2018 – LGPD).</p>

      <h2>Quais dados coletamos</h2>
      <ul>
        <li><strong>Formulário "Solicite um orçamento":</strong> nome, e-mail, telefone e a mensagem que você escrever.</li>
        <li><strong>Antes de abrir o WhatsApp:</strong> nome e telefone, e o assunto do botão que você clicou.</li>
        <li><strong>Origem da visita:</strong> a página do site e os parâmetros de campanha do link (por exemplo, se você veio de um anúncio ou do Instagram).</li>
        <li><strong>Cookies e dados de navegação:</strong> somente se você aceitar, conforme a seção "Cookies".</li>
      </ul>

      <h2>Para que usamos</h2>
      <ul>
        <li>Responder seu contato, enviar orçamentos e agendar visitas técnicas.</li>
        <li>Entender quais canais e campanhas trazem clientes, para melhorar nossa comunicação.</li>
        <li>Medir e otimizar anúncios no Google e na Meta (Facebook e Instagram), quando você aceita os cookies.</li>
      </ul>
      <p>Não vendemos seus dados e não usamos seus contatos para nada além do relacionamento com a {E['nome']}.</p>

      <h2>Onde os dados ficam</h2>
      <p>Os dados dos formulários são enviados de forma segura para uma planilha do Google (Google Workspace) acessada apenas pela nossa equipe. O site é hospedado pela Netlify. As conversas no WhatsApp seguem também as regras do próprio WhatsApp.</p>
      <p>Se você aceitar os cookies, quando você envia um formulário informamos ao Google e à Meta que houve um contato vindo do site, junto com seu telefone, e-mail e nome <strong>criptografados</strong> (transformados em um código que não permite ler o dado original). Isso serve só para medir quais anúncios trazem clientes. Se você recusar os cookies, nada disso é enviado.</p>

      <h2>Por quanto tempo</h2>
      <p>Guardamos seus dados pelo tempo necessário para atender sua solicitação e manter o relacionamento com você, ou até você pedir a exclusão, salvo quando a lei exigir guardar por mais tempo.</p>

      <h2 id="cookies">Cookies</h2>
      <p>Usamos o Google Analytics, o Google Ads e o Pixel da Meta para entender as visitas e medir anúncios. Esses serviços só gravam cookies de análise e publicidade <strong>se você aceitar</strong> no aviso de cookies; o Pixel da Meta nem é carregado antes disso. Se recusar, o site funciona normalmente.</p>
      <p><button type="button" class="btn btn--red" data-abrir-cookies>Alterar minha escolha de cookies</button></p>

      <h2>Seus direitos</h2>
      <p>Pela LGPD, você pode pedir a qualquer momento: confirmação de que tratamos seus dados, acesso, correção, exclusão, informação sobre com quem compartilhamos e revogação do consentimento.</p>
      <p>Para isso, fale com a gente:</p>
      <ul>
        <li>E-mail: <a href="mailto:{E['email']}">{E['email']}</a></li>
        <li>Telefone/WhatsApp: <a href="tel:{E['telefone_link']}">{E['telefone']}</a></li>
      </ul>

      <h2>Alterações</h2>
      <p>Podemos atualizar esta política. A data da última atualização fica sempre no topo desta página.</p>

      <p class="legal__voltar"><a href="/" class="btn btn--ghost-dark">Voltar ao site</a></p>
    </main>''')


# =====================================================================
# robots.txt e sitemap.xml
# =====================================================================

def sitemap():
    urls = ['/'] + ['/' + p['slug'] for p in PRODUTOS]
    itens = ''.join(f'  <url><loc>{URL}{u}</loc><lastmod>{HOJE}</lastmod></url>\n' for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{itens}</urlset>\n'


def escrever(nome, conteudo):
    with open(os.path.join(PUBLIC, nome), 'w') as f:
        f.write(conteudo)
    print('ok', nome)


if __name__ == '__main__':
    escrever('index.html', pagina_inicial())
    for p in PRODUTOS:
        escrever(p['slug'] + '.html', pagina_produto(p))
    escrever('links.html', pagina_links())
    escrever('obrigado.html', pagina_obrigado())
    escrever('404.html', pagina_404())
    escrever('politica-de-privacidade.html', pagina_privacidade())
    escrever('robots.txt', f'User-agent: *\nAllow: /\n\nSitemap: {URL}/sitemap.xml\n')
    escrever('sitemap.xml', sitemap())
