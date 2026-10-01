import { useState, type FormEvent } from "react";

interface ComposerProps {
  placeholder: string;
  disabled?: boolean;
  onSubmit: (text: string) => void;
  variant?: "default" | "question";
}

export function Composer({
  placeholder,
  disabled = false,
  onSubmit,
  variant = "default",
}: ComposerProps) {
  const [value, setValue] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSubmit(trimmed);
    setValue("");
  }

  const isQuestion = variant === "question";

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        className={`flex-1 rounded-full border px-4 py-2 text-sm outline-none focus:ring-2 disabled:bg-gray-100 ${
          isQuestion
            ? "border-indigo-300 focus:ring-indigo-200"
            : "border-gray-300 focus:ring-gray-200"
        }`}
      />
      <button
        type="submit"
        disabled={disabled || !value.trim()}
        className={`rounded-full px-4 py-2 text-sm font-medium text-white disabled:opacity-40 ${
          isQuestion ? "bg-indigo-600" : "bg-gray-900"
        }`}
      >
        {isQuestion ? "Answer" : "Send"}
      </button>
    </form>
  );
}
