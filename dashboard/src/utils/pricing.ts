// Claude model pricing ($ per million tokens)
const MODEL_PRICING: Record<
  string,
  { input: number; output: number; cacheRead: number; cacheCreation: number }
> = {
  "claude-opus-4": { input: 15, output: 75, cacheRead: 1.5, cacheCreation: 18.75 },
  "claude-sonnet-4": { input: 3, output: 15, cacheRead: 0.3, cacheCreation: 3.75 },
  "claude-haiku-4": { input: 0.8, output: 4, cacheRead: 0.08, cacheCreation: 1 },
};

// Match model strings like "claude-opus-4-6", "claude-sonnet-4-6-20250514" to base pricing
function findPricing(model: string) {
  for (const [key, pricing] of Object.entries(MODEL_PRICING)) {
    if (model.startsWith(key)) return pricing;
  }
  // Fallback: sonnet pricing (most common)
  return MODEL_PRICING["claude-sonnet-4"];
}

export function estimateCost(
  model: string,
  input: number,
  output: number,
  cacheRead: number,
  cacheCreation: number,
): number {
  const p = findPricing(model);
  return (
    (input * p.input +
      output * p.output +
      cacheRead * p.cacheRead +
      cacheCreation * p.cacheCreation) /
    1_000_000
  );
}

export function formatCost(cost: number): string {
  if (cost < 0.01) return "<$0.01";
  if (cost < 1) return `$${cost.toFixed(2)}`;
  return `$${cost.toFixed(2)}`;
}
