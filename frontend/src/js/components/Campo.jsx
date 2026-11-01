/** Campo de formulario com rotulo e mensagem de erro. */
export default function Campo({ id, rotulo, erro, children, dica }) {
  return (
    <div className={`field ${erro ? 'field--erro' : ''}`}>
      <label htmlFor={id}>{rotulo}</label>
      {children}
      {erro ? (
        <span className="field__erro">{erro}</span>
      ) : (
        dica && <span className="field__dica">{dica}</span>
      )}
    </div>
  );
}
