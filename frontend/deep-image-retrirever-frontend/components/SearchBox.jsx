import { useState } from "react";

function SearchBox() {
  const [searchQuery, setSearchQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setLoading(true);
    setResults([]); // clear old results

    try {
      const res = await fetch("http://localhost:8000/search-endpoint", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ search_phrase: searchQuery }),
      });

      const data = await res.json();

      // Normalize paths coming from backend (replace '\' with '/')
      const images = (data["retreived images"] || []).map((path) => {
        const normalizedPath = path.replace(/\\/g, "/");
        return {
          url: `http://localhost:8000/${normalizedPath}`,
          name: normalizedPath.split("/").pop(),
        };
      });

      setResults(images);
    } catch (error) {
      console.error("Search error:", error);
      alert("Failed to fetch images. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        textAlign: "center",
        backgroundColor: "#f9fafb",
        minHeight: "100vh",
        paddingBottom: "40px",
      }}
    >
      {/* Search Bar */}
      <form
        onSubmit={handleSend}
        style={{
          padding: "20px",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          gap: "10px",
        }}
      >
        <input
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search images..."
          disabled={loading}
          style={{
            padding: "10px 15px",
            width: "400px",
            borderRadius: "8px",
            border: "1px solid #ccc",
            fontSize: "16px",
            outline: "none",
            opacity: loading ? 0.6 : 1,
          }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "10px 20px",
            borderRadius: "8px",
            border: "none",
            backgroundColor: loading ? "#ccc" : "#007bff",
            color: "white",
            cursor: loading ? "not-allowed" : "pointer",
            fontSize: "16px",
            transition: "background-color 0.3s",
          }}
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {/* Loading Spinner */}
      {loading && (
        <div style={{ marginTop: "40px" }}>
          <div
            style={{
              border: "4px solid #f3f3f3",
              borderTop: "4px solid #007bff",
              borderRadius: "50%",
              width: "50px",
              height: "50px",
              animation: "spin 1s linear infinite",
              margin: "0 auto",
            }}
          ></div>
          <p style={{ marginTop: "20px", color: "#666", fontSize: "18px" }}>
            Loading results...
          </p>
          <style>{`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}</style>
        </div>
      )}

      {/* Results Grid */}
      {!loading && results.length > 0 && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
            gap: "20px",
            padding: "20px 40px",
          }}
        >
          {results.map((img, index) => (
            <div
              key={index}
              style={{
                border: "1px solid #ddd",
                borderRadius: "12px",
                boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                overflow: "hidden",
                backgroundColor: "#fff",
                transition: "transform 0.2s ease-in-out",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.transform = "scale(1.03)")}
              onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
            >
              <img
                src={img.url}
                alt={img.name}
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
                {img.name}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* No Results */}
      {!loading && results.length === 0 && searchQuery && (
        <p style={{ textAlign: "center", color: "#666", marginTop: "20px" }}>
          No images found. Try searching something else.
        </p>
      )}
    </div>
  );
}

export default SearchBox;
