import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ScoreCard } from "@/components/dashboard/ScoreCard";

describe("ScoreCard", () => {
  it("shows score and Strong status for high values", () => {
    render(<ScoreCard label="Technical Score" score={82} />);
    expect(screen.getByText("82")).toBeInTheDocument();
    expect(screen.getByText("Strong")).toBeInTheDocument();
    expect(screen.getByRole("progressbar")).toHaveAttribute("aria-valuenow", "82");
  });

  it("shows Weak status for low values", () => {
    render(<ScoreCard label="Sentiment" score={18} />);
    expect(screen.getByText("Weak")).toBeInTheDocument();
  });
});
