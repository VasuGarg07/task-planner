interface Props {
  name: string;
  small?: boolean;
}

export default function Avatar({ name, small = false }: Props) {
  const parts = name.split(/[.\s-]+/).filter((part) => part !== "");
  const initials = parts
    .slice(0, 2)
    .map((part) => part.charAt(0).toUpperCase())
    .join("");

  return <span className={small ? "avatar small" : "avatar"}>{initials}</span>;
}
