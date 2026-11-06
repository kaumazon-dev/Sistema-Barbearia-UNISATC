/**
 * Converte o ErroApi em erros por campo do formulario.
 *
 * A API devolve as mensagens de validacao do Marshmallow em ingles; aqui so a
 * CHAVE do campo e usada, e a mensagem exibida e a nossa.
 */
export function errosDosCampos(erro, mensagens) {
  if (erro?.codigo !== 'DADOS_INVALIDOS' || !erro.campos) return {};
  const resultado = {};
  Object.keys(erro.campos).forEach((campo) => {
    resultado[campo] = mensagens[campo] || 'Valor inválido.';
  });
  return resultado;
}
