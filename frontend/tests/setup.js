// O Node 22+ tem um localStorage global proprio que, sem --localstorage-file,
// fica indefinido e esconde o do jsdom. Nos testes, um em memoria basta.
const dados = new Map();
globalThis.localStorage = {
  getItem: (chave) => (dados.has(chave) ? dados.get(chave) : null),
  setItem: (chave, valor) => dados.set(chave, String(valor)),
  removeItem: (chave) => dados.delete(chave),
  clear: () => dados.clear()
};
