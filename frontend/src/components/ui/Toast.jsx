import { useState, useEffect } from "react";

let _timer = null;

export default function Toast({ text, type = "success", onClose }) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    if (!visible && onClose) {
      const id = setTimeout(() => {
        onClose();
      }, 300);
      return () => clearTimeout(id);
    }
  }, [visible, onClose]);

  const hide = () => {
    setVisible(false);
  };

  useEffect(() => {
    if (!text || !visible) return;
    if (_timer) clearTimeout(_timer);
    _timer = setTimeout(() => {
      onClose?.();
    }, 3500);
    return () => {
      if (_timer) clearTimeout(_timer);
    };
  }, [text, visible, onClose]);

  if (!text || !visible) return null;

  return (
    <div
      className={`fixed left-1/2 top-20 z-50 -translate-x-1/2 rounded-xl border px-5 py-3 shadow-xl text-sm font-medium transition-all duration-300 ${
        type === "error"
          ? "border-red-200 bg-red-50 text-red-800"
          : "border-emerald-200 bg-emerald-50 text-emerald-800"
      }`}
      onClick={hide}
    >
      <div className="flex items-center gap-2">{text}</div>
    </div>
  );
}
