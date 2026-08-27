/* Elih — gerador de propostas. Três etapas: upload, confirmação, download. */

const $ = (id) => document.getElementById(id);
const MAX_COMPARAR = 4;
const MAX_ARQUIVOS = 5;

const estado = {
  sessao: null,
  /** PDFs na fila, um por operadora. */
  arquivos: [],
  analise: null,
  regiao: null,
  /** Ordem importa: o primeiro selecionado é o plano recomendado. */
  planos: [],
  cidades: new Set(),
  /** { "0:0": { abrangencia, coparticipacao } } */
  atributos: {},
  escolhas: {
    possui_plano: 'nao',
    tipo_cnpj: '',
    usar_ia: 'sim',
  },
  passoConfig: 1, // Passo atual dentro da configuração (1, 2 ou 3)
};

/* ------------------------------------------------------------- helpers -- */

function mostra(etapa) {
  ['etapa-upload', 'etapa-config', 'etapa-pronto'].forEach((id) =>
    $(id).classList.toggle('oculto', id !== etapa)
  );
  if (etapa === 'etapa-config') {
    mudaSubPasso(1);
  }
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function carregando(ativo, titulo, desc) {
  $('carregando').classList.toggle('oculto', !ativo);
  if (titulo) $('carregando-t').textContent = titulo;
  if (desc) $('carregando-d').textContent = desc;
}

function erro(msg) {
  const el = $('erro');
  el.textContent = msg;
  el.classList.toggle('oculto', !msg);
  if (msg) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])
  );
}

/**
 * Lê a resposta da API tolerando o que NÃO é JSON.
 *
 * Quando o upload estoura o limite do proxy, ou o container reinicia, quem
 * responde é o proxy — com uma página HTML. Fazer resp.json() nesse caso
 * mostrava "Unexpected token '<'", que não diz nada. Aqui o erro vira o código
 * HTTP e o motivo provável.
 */
async function leResposta(resp, contexto) {
  const bruto = await resp.text();
  let dados = null;
  try {
    dados = JSON.parse(bruto);
  } catch {
    /* veio HTML ou texto puro */
  }

  if (resp.ok && dados) return dados;

  if (dados && dados.detail) throw new Error(dados.detail);

  if (resp.status === 413) {
    throw new Error(
      'O servidor recusou o envio por tamanho. Os PDFs de rede completa passam ' +
        'de 35 MB cada — aumente o limite de upload do proxy (client_max_body_size).'
    );
  }
  if (resp.status === 502 || resp.status === 504) {
    throw new Error(
      `O servidor não respondeu a tempo (${resp.status}). Com vários PDFs grandes ` +
        'a leitura demora; aumente o timeout do proxy.'
    );
  }
  if (!resp.ok) {
    throw new Error(`${contexto}: o servidor respondeu ${resp.status}.`);
  }
  throw new Error(`${contexto}: resposta inesperada do servidor.`);
}

/** Grupos de chips com seleção única, ligados por data-grupo/data-valor. */
function ligaChips(raiz) {
  raiz.querySelectorAll('.chip[data-grupo]').forEach((chip) => {
    chip.onclick = () => {
      const grupo = chip.dataset.grupo;
      raiz
        .querySelectorAll(`.chip[data-grupo="${grupo}"]`)
        .forEach((c) => c.classList.remove('ativo'));
      chip.classList.add('ativo');
      estado.escolhas[grupo] = chip.dataset.valor;
      limpaErrosValidacao();
    };
  });
}

/* --- Lógica de Validação e Sub-Passos (UI/UX Pro Max) --- */

function limpaErrosValidacao() {
  document.querySelectorAll('.campo.erro-validacao').forEach((el) => {
    el.classList.remove('erro-validacao');
  });
  erro('');
}

function mudaSubPasso(passo) {
  estado.passoConfig = passo;

  [1, 2, 3].forEach((p) => {
    $(`sub-etapa-${p}`).classList.toggle('oculto', p !== passo);
    const indicator = $(`step-ind-${p}`);
    if (indicator) {
      indicator.classList.toggle('active', p === passo);
      indicator.classList.toggle('completed', p < passo);
    }
    const line = $(`step-line-${p}`);
    if (line) {
      line.classList.toggle('completed', p < passo);
    }
  });

  limpaErrosValidacao();

  const btnAnterior = $('btn-passo-anterior');
  const btnProximo = $('btn-passo-proximo');

  if (passo === 1) {
    btnAnterior.style.display = 'none';
    btnProximo.textContent = 'Avançar →';
  } else {
    btnAnterior.style.display = 'block';
    if (passo === 3) {
      btnProximo.textContent = 'Gerar proposta →';
    } else {
      btnProximo.textContent = 'Avançar →';
    }
  }
}

function validaPasso(passo) {
  limpaErrosValidacao();
  if (passo === 1) {
    if (!estado.planos.length) {
      const campo = $('campo-plano');
      campo.classList.add('erro-validacao');
      campo.scrollIntoView({ behavior: 'smooth', block: 'center' });
      erro('Marque pelo menos um plano para continuar.');
      return false;
    }
  } else if (passo === 2) {
    if (!estado.regiao) {
      const campo = $('campo-regiao');
      campo.classList.add('erro-validacao');
      campo.scrollIntoView({ behavior: 'smooth', block: 'center' });
      erro('Escolha onde o cliente vai usar o plano para continuar.');
      return false;
    }
  } else if (passo === 3) {
    for (const id of estado.planos) {
      const o = estado.analise.opcoes.find((x) => x.id === id);
      if (!o) continue;
      for (const campo of o.faltando) {
        if (!(estado.atributos[id] || {})[campo]) {
          const el = $('campo-atributos');
          el.classList.add('erro-validacao');
          el.scrollIntoView({ behavior: 'smooth', block: 'center' });
          erro(
            `Confirme ${campo === 'abrangencia' ? 'a abrangência' : 'a coparticipação'} de ` +
              `${o.plano} — não está escrita no PDF e eu não vou supor.`
          );
          return false;
        }
      }
    }
  }
  return true;
}

// Configurar cliques diretos no stepper
[1, 2, 3].forEach((p) => {
  const indicator = $(`step-ind-${p}`);
  if (indicator) {
    indicator.onclick = () => {
      if (p < estado.passoConfig) {
        mudaSubPasso(p);
      } else if (p > estado.passoConfig) {
        let val = true;
        for (let step = estado.passoConfig; step < p; step++) {
          if (!validaPasso(step)) {
            val = false;
            break;
          }
        }
        if (val) {
          mudaSubPasso(p);
        }
      }
    };
  }
});

/* -------------------------------------------------------------- upload -- */

const drop = $('drop');
const inputArquivo = $('arquivo');

drop.onclick = () => inputArquivo.click();
inputArquivo.onchange = () => {
  adiciona([...inputArquivo.files]);
  inputArquivo.value = ''; // permite reescolher o mesmo arquivo
};

['dragenter', 'dragover'].forEach((ev) =>
  drop.addEventListener(ev, (e) => {
    e.preventDefault();
    drop.classList.add('sobre');
  })
);
['dragleave', 'drop'].forEach((ev) =>
  drop.addEventListener(ev, (e) => {
    e.preventDefault();
    drop.classList.remove('sobre');
  })
);
drop.addEventListener('drop', (e) => adiciona([...e.dataTransfer.files]));

function adiciona(novos) {
  const pdfs = novos.filter((f) => f.name.toLowerCase().endsWith('.pdf'));
  if (pdfs.length < novos.length) erro('Ignorei os arquivos que não eram PDF.');
  else erro('');

  for (const f of pdfs) {
    if (estado.arquivos.length >= MAX_ARQUIVOS) {
      erro(`Máximo de ${MAX_ARQUIVOS} PDFs por proposta.`);
      break;
    }
    const repetido = estado.arquivos.some((x) => x.name === f.name && x.size === f.size);
    if (!repetido) estado.arquivos.push(f);
  }
  pintaArquivos();
}

function pintaArquivos() {
  const n = estado.arquivos.length;
  $('lista-arquivos').innerHTML = estado.arquivos
    .map(
      (f, i) => `
      <li class="arq">
        <span class="arq__n">${i + 1}</span>
        <span class="arq__corpo">
          <span class="arq__nome">${esc(f.name)}</span>
          <span class="arq__tam">${(f.size / 1048576).toFixed(1)} MB</span>
        </span>
        <button type="button" class="arq__x" data-i="${i}" aria-label="Remover">×</button>
      </li>`
    )
    .join('');

  $('lista-arquivos')
    .querySelectorAll('.arq__x')
    .forEach((b) => {
      b.onclick = () => {
        estado.arquivos.splice(Number(b.dataset.i), 1);
        pintaArquivos();
      };
    });

  $('btn-analisar').classList.toggle('oculto', n === 0);
  $('qtd-arquivos').textContent = n === 1 ? '1 cotação' : `${n} cotações`;
  $('drop-titulo').textContent = n
    ? n >= MAX_ARQUIVOS
      ? 'Limite de 5 PDFs atingido'
      : 'Adicionar mais um PDF'
    : 'Toque para escolher os PDFs';
  $('drop-desc').textContent = n
    ? `${n} de ${MAX_ARQUIVOS} na fila`
    : `ou arraste os arquivos aqui · até ${MAX_ARQUIVOS}`;
  drop.classList.toggle('carregado', n > 0);
}

$('btn-analisar').onclick = () => analisa();

async function analisa() {
  if (!estado.arquivos.length) return erro('Escolha ao menos um PDF.');
  erro('');

  const n = estado.arquivos.length;
  carregando(
    true,
    n > 1 ? `Lendo ${n} cotações…` : 'Lendo o PDF…',
    'Extraindo valores, rede credenciada e reembolso'
  );

  const form = new FormData();
  estado.arquivos.forEach((f) => form.append('arquivos', f));

  try {
    const resp = await fetch('/api/analisar', { method: 'POST', body: form });
    const dados = await leResposta(resp, 'Falha ao ler os PDFs');
    estado.sessao = dados.sessao;
    estado.analise = dados;
    // Com mais de um arquivo, a intenção é comparar: já marca tudo (até o limite).
    estado.planos = dados.opcoes.slice(0, dados.opcoes.length > 1 ? MAX_COMPARAR : 1).map((o) => o.id);
    estado.atributos = {};
    montaConfig(dados);
    mostra('etapa-config');
  } catch (e) {
    erro(e.message);
  } finally {
    carregando(false);
  }
}

/* ---------------------------------------------------------- etapa dois -- */

function montaConfig(d) {
  const nArq = (d.arquivos || []).length;
  const partes = [
    nArq > 1 ? `${nArq} PDFs` : null,
    `${d.opcoes.length} ${d.opcoes.length === 1 ? 'plano' : 'planos'}`,
    d.referencia ? `tabela ${d.referencia}` : null,
  ].filter(Boolean);
  $('resumo-leitura').innerHTML =
    `Li <strong>${esc(partes.join(' · '))}</strong>. ` +
    `Operadoras: ${esc(d.operadoras.join(', '))}. ` +
    `${d.regioes.length} regiões de rede credenciada.`;

  montaPlanos(d);
  montaRegioes(d);
  ligaChips($('etapa-config'));
}

function montaPlanos(d) {
  $('campo-plano').hidden = d.opcoes.length < 2;
  $('planos').innerHTML = d.opcoes
    .map(
      (o) => `
      <button type="button" class="opcao-plano" data-plano="${esc(o.id)}">
        <span class="opcao-plano__marca"></span>
        <span class="opcao-plano__corpo">
          <span class="opcao-plano__operadora">${esc(o.operadora)}</span>
          <span class="opcao-plano__nome">${esc(o.plano)}</span>
          <span class="opcao-plano__meta">${esc(o.acomodacao)}${
            o.total ? ' · ' + esc(o.total) : ''
          }${o.abrangencia ? ' · ' + esc(o.abrangencia) : ''}</span>
        </span>
      </button>`
    )
    .join('');

  $('planos')
    .querySelectorAll('.opcao-plano')
    .forEach((btn) => {
      btn.onclick = () => {
        const id = btn.dataset.plano;
        const i = estado.planos.indexOf(id);
        if (i >= 0) {
          if (estado.planos.length === 1) return erro('Deixe pelo menos um plano marcado.');
          estado.planos.splice(i, 1);
        } else {
          if (estado.planos.length >= MAX_COMPARAR)
            return erro(`Dá para comparar no máximo ${MAX_COMPARAR} planos por proposta.`);
          estado.planos.push(id);
        }
        limpaErrosValidacao();
        pintaPlanos();
        montaAtributos();
      };
    });

  pintaPlanos();
  montaAtributos();
}

function pintaPlanos() {
  $('planos')
    .querySelectorAll('.opcao-plano')
    .forEach((btn) => {
      const pos = estado.planos.indexOf(btn.dataset.plano);
      btn.classList.toggle('ativo', pos >= 0);
      btn.querySelector('.opcao-plano__marca').textContent =
        pos === 0 ? '★' : pos > 0 ? String(pos + 1) : '';
      btn.classList.toggle('opcao-plano--rec', pos === 0);
    });

  const n = estado.planos.length;
  $('ajuda-plano').textContent =
    n > 1
      ? `${n} planos marcados — a proposta vai ter a página de comparação, com ★ como recomendado.`
      : 'O primeiro que você marcar é o recomendado. Marque 2 a 4 para gerar a página de comparação lado a lado.';
}

/** Só pede o que falta, e só dos planos que o corretor realmente selecionou. */
function montaAtributos() {
  const pendentes = estado.planos
    .map((id) => estado.analise.opcoes.find((o) => o.id === id))
    .filter((o) => o && o.faltando.length);

  $('campo-atributos').classList.toggle('oculto', !pendentes.length);
  if (!pendentes.length) return;

  const OPCOES = {
    abrangencia: [['Nacional', 'Nacional'], ['Estadual', 'Estadual'], ['Regional', 'Regional']],
    coparticipacao: [
      ['Sem coparticipação', 'Sem'],
      ['Coparticipação parcial', 'Parcial'],
      ['Com coparticipação', 'Com'],
    ],
  };
  const ROTULO = { abrangencia: 'Abrangência', coparticipacao: 'Coparticipação' };

  $('atributos').innerHTML = pendentes
    .map(
      (o) => `
      <div class="atr">
        <div class="atr__plano">${esc(o.operadora)} · ${esc(o.plano)}</div>
        ${o.faltando
          .map(
            (campo) => `
          <div class="atr__linha">
            <span class="atr__rot">${ROTULO[campo]}</span>
            <span class="opcoes">
              ${OPCOES[campo]
                .map(
                  ([v, rotulo]) =>
                    `<button type="button" class="chip chip--mini${
                      (estado.atributos[o.id] || {})[campo] === v ? ' ativo' : ''
                    }" data-opcao="${esc(o.id)}" data-campo="${campo}" data-v="${esc(
                      v
                    )}">${esc(rotulo)}</button>`
                )
                .join('')}
            </span>
          </div>`
          )
          .join('')}
      </div>`
    )
    .join('');

  $('atributos')
    .querySelectorAll('.chip[data-opcao]')
    .forEach((chip) => {
      chip.onclick = () => {
        const { opcao, campo, v } = chip.dataset;
        $('atributos')
          .querySelectorAll(`.chip[data-opcao="${opcao}"][data-campo="${campo}"]`)
          .forEach((c) => c.classList.remove('ativo'));
        chip.classList.add('ativo');
        estado.atributos[opcao] = { ...(estado.atributos[opcao] || {}), [campo]: v };
        limpaErrosValidacao();
      };
    });
}

function montaRegioes(d) {
  const ordem = ['SÃO PAULO', 'INTERIOR'];
  const regioes = [...d.regioes].sort(
    (a, b) =>
      (ordem.indexOf(a.nome) + 1 || 99) - (ordem.indexOf(b.nome) + 1 || 99) ||
      a.nome.localeCompare(b.nome)
  );
  $('regioes').innerHTML = regioes
    .map(
      (r) =>
        `<button type="button" class="chip" data-regiao="${esc(r.nome)}">${esc(
          rotuloRegiao(r.nome)
        )}<small>${r.cidades.length} ${
          r.nome === 'SÃO PAULO' ? 'zonas' : 'cidades'
        }</small></button>`
    )
    .join('');

  $('regioes')
    .querySelectorAll('.chip[data-regiao]')
    .forEach((chip) => {
      chip.onclick = () => {
        $('regioes')
          .querySelectorAll('.chip')
          .forEach((c) => c.classList.remove('ativo'));
        chip.classList.add('ativo');
        estado.regiao = chip.dataset.regiao;
        estado.cidades.clear();
        montaCidades(d.regioes.find((r) => r.nome === estado.regiao));
        limpaErrosValidacao();
      };
    });
}

function rotuloRegiao(nome) {
  if (nome === 'SÃO PAULO') return 'São Paulo — capital';
  if (nome === 'INTERIOR') return 'Interior de SP';
  return nome
    .toLowerCase()
    .replace(/(^|\s|-)([a-zà-ú])/g, (m, a, b) => a + b.toUpperCase())
    .replace(/\bAbcd\b/, 'ABCD');
}

function montaCidades(regiao) {
  const campo = $('campo-cidades');
  if (!regiao || regiao.cidades.length < 2) {
    campo.hidden = true;
    return;
  }
  campo.hidden = false;
  $('cidades').innerHTML = regiao.cidades
    .map((c) => `<button type="button" class="chip" data-cidade="${esc(c)}">${esc(c)}</button>`)
    .join('');
  $('cidades')
    .querySelectorAll('.chip[data-cidade]')
    .forEach((chip) => {
      chip.onclick = () => {
        const c = chip.dataset.cidade;
        if (estado.cidades.has(c)) estado.cidades.delete(c);
        else estado.cidades.add(c);
        chip.classList.toggle('ativo', estado.cidades.has(c));
      };
    });
}

/* --------------------------------------------------------- etapa três -- */

async function gerarProposta() {
  erro('');
  carregando(
    true,
    'Montando a proposta…',
    estado.planos.length > 1
      ? 'Comparativo, rede, objeções e diagramação'
      : 'Copy, rede, tabelas e diagramação em 4 páginas'
  );

  const form = new FormData();
  form.append('sessao', estado.sessao);
  form.append('regiao', estado.regiao);
  form.append('comparar', estado.planos.join('|'));
  form.append('cidades', [...estado.cidades].join('|'));
  form.append('atributos', JSON.stringify(estado.atributos));
  Object.entries(estado.escolhas).forEach(([k, v]) => form.append(k, v));

  try {
    const resp = await fetch('/api/gerar', { method: 'POST', body: form });
    const dados = await leResposta(resp, 'Falha ao gerar a proposta');

    $('link-download').href = dados.url;
    $('link-download').setAttribute('download', dados.nome);
    $('stats-final').innerHTML = `
      <div class="stat"><div class="stat__n">${dados.paginas}</div>
        <div class="stat__r">páginas no PDF</div></div>
      <div class="stat"><div class="stat__n">${dados.comparados}</div>
        <div class="stat__r">${
          dados.comparados > 1 ? 'planos comparados lado a lado' : 'plano na proposta'
        }</div></div>
      <div class="stat"><div class="stat__n">${dados.objecoes}</div>
        <div class="stat__r">quebras de objeção incluídas</div></div>
      <div class="stat"><div class="stat__n">${dados.hospitais}</div>
        <div class="stat__r">hospitais na região escolhida</div></div>`;
    mostra('etapa-pronto');
  } catch (e) {
    erro(e.message);
  } finally {
    carregando(false);
  }
}

// Botões de navegação do stepper
$('btn-passo-anterior').onclick = () => {
  if (estado.passoConfig > 1) {
    mudaSubPasso(estado.passoConfig - 1);
  }
};

$('btn-passo-proximo').onclick = () => {
  if (validaPasso(estado.passoConfig)) {
    if (estado.passoConfig < 3) {
      mudaSubPasso(estado.passoConfig + 1);
    } else {
      gerarProposta();
    }
  }
};

$('btn-voltar').onclick = () => {
  erro('');
  mostra('etapa-upload');
};
$('btn-ajustar').onclick = () => mostra('etapa-config');
$('btn-novo').onclick = () => location.reload();

/* ------------------------------------------------------------ PWA -- */

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () =>
    navigator.serviceWorker.register('/sw.js').catch(() => {})
  );
}

/* Chrome/Edge/Android: o navegador avisa quando o app é instalável e nos deixa
   disparar o diálogo na hora que quisermos. */
let promptInstalacao = null;

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  promptInstalacao = e;
  $('btn-instalar').classList.remove('oculto');
});

$('btn-instalar').onclick = async () => {
  if (!promptInstalacao) return;
  promptInstalacao.prompt();
  const { outcome } = await promptInstalacao.userChoice;
  promptInstalacao = null;
  if (outcome === 'accepted') $('btn-instalar').classList.add('oculto');
};

window.addEventListener('appinstalled', () => {
  promptInstalacao = null;
  $('btn-instalar').classList.add('oculto');
  localStorage.setItem('cotador-instalado', '1');
});

/* iOS não expõe beforeinstallprompt: no Safari a instalação é manual, então
   mostramos a instrução uma única vez. */
(function dicaIOS() {
  const ehIOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
  const jaEstaNoApp =
    window.matchMedia('(display-mode: standalone)').matches || navigator.standalone === true;
  const jaDispensou = localStorage.getItem('cotador-dica-ios') === '1';

  if (!ehIOS || jaEstaNoApp || jaDispensou) return;
  const banner = $('instalar-ios');
  banner.classList.remove('oculto');
  $('fechar-ios').onclick = () => {
    banner.classList.add('oculto');
    localStorage.setItem('cotador-dica-ios', '1');
  };
})();
