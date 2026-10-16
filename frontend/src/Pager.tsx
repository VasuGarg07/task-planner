import { ChevronLeft, ChevronRight } from "lucide-react";

import { PAGE_SIZE } from "./api";

interface Props {
  page: number;
  count: number;
  onPage: (page: number) => void;
}

export default function Pager({ page, count, onPage }: Props) {
  return (
    <div className="row pager">
      <button disabled={page === 1} onClick={() => onPage(page - 1)}>
        <ChevronLeft size={16} /> Previous
      </button>
      <span className="muted">Page {page}</span>
      <button disabled={count < PAGE_SIZE} onClick={() => onPage(page + 1)}>
        Next <ChevronRight size={16} />
      </button>
    </div>
  );
}
