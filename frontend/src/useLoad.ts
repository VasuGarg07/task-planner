import { useCallback, useEffect, useState } from "react";

import { errorMessage } from "./api";

export function useLoad<T>(load: () => Promise<T>, deps: readonly unknown[]) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState("");

  const reload = useCallback(() => {
    setError("");
    load()
      .then(setData)
      .catch((caught) => setError(errorMessage(caught)));
  }, deps);

  useEffect(reload, [reload]);

  async function run(action: () => Promise<unknown>): Promise<void> {
    try {
      await action();
      reload();
    } catch (caught) {
      setError(errorMessage(caught));
    }
  }

  return { data, error, reload, run };
}
