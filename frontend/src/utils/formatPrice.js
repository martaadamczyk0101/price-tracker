export function formatPrice(value, currency = "zł") {
  if (value == null) return "";

  return `${Number(value).toFixed(2)} ${currency}`;
}
