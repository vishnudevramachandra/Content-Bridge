export function ErrorBanner({ detail }: { detail: string }) {
  return (
    <div className="flex justify-center">
      <div className="max-w-[90%] rounded-lg border border-red-300 bg-red-50 px-3 py-2 text-xs text-red-700">
        ⚠ {detail}
      </div>
    </div>
  );
}
