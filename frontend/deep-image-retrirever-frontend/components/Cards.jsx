// src/components/Cards.jsx
import React from "react";

function Cards({ images }) {
  if (!images || images.length === 0) {
    return (
      <p style={{ textAlign: "center", color: "#666", marginTop: "20px" }}>
        No images found. Try searching something else.
      </p>
    );
  }

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
        gap: "20px",
        padding: "20px 40px",
      }}
    >
      {images.map((img, index) => (
        <div
          key={index}
          style={{
            border: "1px solid #ddd",
            borderRadius: "12px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
            overflow: "hidden",
            backgroundColor: "#fff",
            transition: "transform 0.2s ease-in-out",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.transform = "scale(1.03)")}
          onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
        >
          <img
            src={img.url || img} // support either string URLs or objects {url, name}
            alt={img.name || `Image ${index}`}
            style={{
              width: "100%",
              height: "200px",
              objectFit: "cover",
            }}
          />
          <div
            style={{
              padding: "10px",
              textAlign: "center",
              fontWeight: "500",
              fontSize: "16px",
              color: "#333",
            }}
          >
            {img.name || `Image ${index + 1}`}
          </div>
        </div>
      ))}
    </div>
  );
}

export default Cards;
