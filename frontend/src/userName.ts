import type { User } from "./api";

export function userName(users: User[], id: number | null, fallback: string): string {
  const user = users.find((candidate) => candidate.id === id);
  return user === undefined ? fallback : user.username;
}
