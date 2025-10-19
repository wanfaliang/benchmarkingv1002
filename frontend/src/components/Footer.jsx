import React from "react";

export default function Footer() {
  const year = new Date().getFullYear();
  return (
    <footer style={{
      padding: "1rem",
      textAlign: "center",
      fontSize: "14px",
      opacity: 0.8,
      borderTop: "1px solid #e0e0e0",
      marginTop: "2rem"
    }}>
      <a href="/privacy-policy.html" style={{ margin: "0 0.5rem" }}>Privacy Policy</a> ·
      <a href="/terms-of-service.html" style={{ margin: "0 0.5rem" }}>Terms of Service</a>
      <div style={{ marginTop: "0.5rem" }}>© {year} Finexus</div>
    </footer>
  );
}
