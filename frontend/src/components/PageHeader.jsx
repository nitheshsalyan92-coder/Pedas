export default function PageHeader({ eyebrow, title, text, children }) {
  return (
    <header className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
      <div className="max-w-3xl">
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-accent">{eyebrow}</p>
        <h1 className="mt-2 font-display text-3xl font-bold tracking-tight text-navy sm:text-4xl">{title}</h1>
        {text ? <p className="mt-3 text-base leading-7 text-slate-600">{text}</p> : null}
      </div>
      {children ? <div className="flex flex-wrap gap-2">{children}</div> : null}
    </header>
  );
}
