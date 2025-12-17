import React from "react";

const Footer: React.FC = () => {
  const year = new Date().getFullYear();

  return (
    <footer
      className="
        w-full
        border-t border-slate-300
        bg-slate-50
        text-slate-600
        text-sm
        mt-8
        px-4 py-4
        text-center
      "
    >
      <div className="space-x-2">
        <a
          href="/privacy-policy.html"
          className="hover:text-slate-900 underline-offset-2 hover:underline"
        >
          Privacy Policy
        </a>
        <span className="text-slate-400">·</span>
        <a
          href="/terms-of-service.html"
          className="hover:text-slate-900 underline-offset-2 hover:underline"
        >
          Terms of Service
        </a>
      </div>

      <div className="text-slate-500 mt-2">
        © {year} Finexus
      </div>
    </footer>
  );
};

export default Footer;
