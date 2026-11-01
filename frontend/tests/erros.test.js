import { describe, expect, it } from 'vitest';
import { ErroApi } from '../src/js/api/http';
import { errosDosCampos } from '../src/js/utils/erros';

describe('errosDosCampos', () => {
  const mensagens = { email: 'Informe um e-mail válido.' };

  it('troca a mensagem em ingles do Marshmallow pela nossa, pela chave do campo', () => {
    const erro = new ErroApi(422, 'DADOS_INVALIDOS', 'Dados de entrada inválidos.', {
      email: ['Not a valid email address.'],
      senha: ['Shorter than minimum length 8.']
    });
    expect(errosDosCampos(erro, mensagens)).toEqual({
      email: 'Informe um e-mail válido.',
      senha: 'Valor inválido.'
    });
  });

  it('erro de negocio nao vira erro de campo', () => {
    const conflito = new ErroApi(409, 'CONFLITO', 'João já tem agendamento.');
    expect(errosDosCampos(conflito, mensagens)).toEqual({});
  });
});
