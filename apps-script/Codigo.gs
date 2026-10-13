/**
 * Solucionne – recebe os formulários do site e grava cada envio numa linha da planilha:
 *   - "Solicite um orçamento"  → aba Orçamentos (com e-mail de aviso)
 *   - popup antes do WhatsApp  → aba Leads WhatsApp
 *
 * Instalação: veja apps-script/LEIAME.md
 */

// ===== Configurações =====
const EMAIL_AVISO = 'vendas@solucionne.com.br'; // recebe um e-mail a cada orçamento; deixe '' para desligar
const AVISAR_LEADS_WHATSAPP = false;           // true = também manda e-mail a cada lead do WhatsApp
// A senha NÃO fica no código: vai em Configurações do projeto → Propriedades do script,
// com o nome SEGREDO_FORMULARIO (o mesmo valor de FORM_SECRET na Netlify).
const PROPRIEDADE_SEGREDO = 'SEGREDO_FORMULARIO';

// Abas criadas automaticamente no primeiro envio de cada tipo
const ABAS = {
  orcamento: {
    nome: 'Orçamentos',
    colunas: ['Data/hora', 'Nome', 'E-mail', 'Telefone', 'Mensagem',
      'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'Página'],
    campos: ['nome', 'email', 'telefone', 'mensagem',
      'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'pagina'],
    obrigatorios: ['nome', 'email', 'telefone', 'mensagem']
  },
  whatsapp: {
    nome: 'Leads WhatsApp',
    colunas: ['Data/hora', 'Nome', 'Telefone', 'Interesse',
      'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'Página'],
    campos: ['nome', 'telefone', 'interesse',
      'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'pagina'],
    obrigatorios: ['nome', 'telefone']
  }
};
const LIMITE_TEXTO = 2000;

/**
 * Recebe o POST da Netlify Function (netlify/functions/orcamento.mjs) em JSON.
 * Só aceita envios que trazem a senha certa.
 */
function doPost(e) {
  try {
    const bruto = JSON.parse((e && e.postData && e.postData.contents) || '{}');

    const segredo = PropertiesService.getScriptProperties().getProperty(PROPRIEDADE_SEGREDO);
    if (!segredo) return responder_(false, 'Senha do formulário não configurada no Apps Script.');
    if (bruto.segredo !== segredo) return responder_(false, 'Não autorizado.');

    const dados = lerDados_(bruto);

    // Campo "empresa" é invisível no site: se veio preenchido, é robô. Responde ok e descarta.
    if (dados.empresa) return responder_(true);

    const tipo = dados.tipo === 'whatsapp' ? 'whatsapp' : 'orcamento';
    const config = ABAS[tipo];
    if (config.obrigatorios.some((campo) => !dados[campo])) {
      return responder_(false, 'Preencha os campos obrigatórios.');
    }

    const linha = [new Date()].concat(config.campos.map((campo) => limpar_(dados[campo])));

    // Evita que dois envios simultâneos se sobreponham na planilha
    const trava = LockService.getScriptLock();
    trava.waitLock(10000);
    try {
      aba_(config).appendRow(linha);
    } finally {
      trava.releaseLock();
    }

    if (tipo === 'orcamento' || AVISAR_LEADS_WHATSAPP) avisarPorEmail_(dados, tipo);
    return responder_(true);
  } catch (erro) {
    console.error(erro);
    return responder_(false, 'Erro ao salvar. Tente novamente.');
  }
}

/** Abrir a URL no navegador mostra que o script está no ar. */
function doGet() {
  return ContentService.createTextOutput('Formulário Solucionne: ativo.');
}

/**
 * Rode esta função UMA VEZ pelo editor (botão "Executar") para autorizar o script
 * e conferir se a linha de teste aparece na planilha.
 */
function testar() {
  const resposta = doPost({
    postData: {
      contents: JSON.stringify({
        nome: 'Teste do script', email: 'teste@exemplo.com', telefone: '(31) 90000-0000',
        mensagem: 'Linha de teste – pode apagar.', pagina: 'teste manual',
        segredo: PropertiesService.getScriptProperties().getProperty(PROPRIEDADE_SEGREDO)
      })
    }
  });
  console.log(resposta.getContent());
}

// ===== Funções internas =====

function lerDados_(bruto) {
  const dados = {};
  ['tipo', 'interesse', 'nome', 'email', 'telefone', 'mensagem', 'empresa', 'pagina',
   'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'].forEach((campo) => {
    dados[campo] = String(bruto[campo] || '').trim().slice(0, LIMITE_TEXTO);
  });
  return dados;
}

/** Impede que um texto como "=IMPORTXML(...)" vire fórmula na planilha. */
function limpar_(valor) {
  const texto = String(valor || '');
  return /^[=+\-@\t\r]/.test(texto) ? "'" + texto : texto;
}

function aba_(config) {
  const planilha = SpreadsheetApp.getActiveSpreadsheet();
  let aba = planilha.getSheetByName(config.nome);
  if (!aba) {
    aba = planilha.insertSheet(config.nome);
    aba.appendRow(config.colunas);
    aba.getRange(1, 1, 1, config.colunas.length).setFontWeight('bold').setBackground('#A01217');
    aba.setFrozenRows(1);
    aba.getRange('A:A').setNumberFormat('dd/MM/yyyy HH:mm');
  }
  return aba;
}

function avisarPorEmail_(dados, tipo) {
  if (!EMAIL_AVISO) return;
  const ehWhatsApp = tipo === 'whatsapp';
  try {
    MailApp.sendEmail({
      to: EMAIL_AVISO,
      replyTo: dados.email || EMAIL_AVISO,
      subject: (ehWhatsApp ? 'Novo lead do WhatsApp – ' : 'Novo orçamento pelo site – ') + dados.nome,
      body: [
        'Nome: ' + dados.nome,
        'Telefone: ' + dados.telefone,
        ehWhatsApp ? 'Interesse: ' + dados.interesse : 'E-mail: ' + dados.email,
        '',
        ehWhatsApp ? '' : 'Mensagem:\n' + dados.mensagem,
        '',
        'Origem: ' + (dados.utm_source || 'direto') + (dados.utm_campaign ? ' / ' + dados.utm_campaign : ''),
        '',
        'Todos os envios: ' + SpreadsheetApp.getActiveSpreadsheet().getUrl()
      ].join('\n')
    });
  } catch (erro) {
    // O envio já foi salvo; falha no e-mail não deve dar erro para o visitante
    console.error('Falha ao enviar e-mail de aviso:', erro);
  }
}

function responder_(ok, mensagem) {
  return ContentService
    .createTextOutput(JSON.stringify({ ok: ok, mensagem: mensagem || '' }))
    .setMimeType(ContentService.MimeType.JSON);
}
