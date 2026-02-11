interface WorkInstructionsProps {
  instructions: string[];
}

export default function WorkInstructions({
  instructions,
}: WorkInstructionsProps) {
  if (instructions.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <h3 className="mb-3 text-sm font-semibold text-gray-900">
          Work Instructions
        </h3>
        <p className="text-sm text-abn-grey">No work instructions uploaded</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-sm font-semibold text-gray-900">
        Work Instructions ({instructions.length})
      </h3>
      <ol className="space-y-3">
        {instructions.map((instruction, idx) => (
          <li key={idx} className="flex items-start gap-3">
            {/* Step number in teal circle */}
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-abn-teal text-xs font-bold text-white">
              {idx + 1}
            </span>
            <p className="text-sm leading-relaxed text-gray-700">
              {instruction}
            </p>
          </li>
        ))}
      </ol>
    </div>
  );
}
