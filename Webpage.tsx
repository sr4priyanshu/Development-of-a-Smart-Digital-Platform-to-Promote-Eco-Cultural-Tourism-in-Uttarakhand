import { useState, useEffect, useMemo } from "react";
import { Destination, DestinationCard } from "@/components/DestinationCard";
import { DestinationModal } from "@/components/DestinationModal";
import { SearchBar } from "@/components/SearchBar";
import { FilterControls } from "@/components/FilterControls";
import MapView from "@/components/MapView";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Map, Grid, Heart } from "lucide-react";
import { toast } from "sonner";
import heroImage from "@/assets/uttarakhand-hero.jpg";

// --- Supabase Imports & Client Setup ---
import { createClient } from "@supabase/supabase-js";

// ⚠️ IMPORTANT: Replace with your actual Supabase project URL
const supabaseUrl = "https://uzersrwjelicaujpoxod.supabase.co"; 
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

// Check if credentials are placeholders
if (supabaseUrl === "https://uzersrwjelicaujpoxod.supabase.co") {
  console.warn("Supabase URL is not set. Please update it in your component.");
}
if (!supabaseKey) {
  console.warn("VITE_SUPABASE_ANON_KEY is missing from your .env file.");
}

const supabase = createClient(supabaseUrl, supabaseKey);
// --- End of Supabase Setup ---

const Index = () => {
  const [destinations, setDestinations] = useState<Destination[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [sortBy, setSortBy] = useState("name");
  const [selectedDestination, setSelectedDestination] = useState<Destination | null>(null);
  const [favorites, setFavorites] = useState<number[]>([]);
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);

  // Load data from Supabase
  useEffect(() => {
    const fetchDestinations = async () => {
      const { data, error } = await supabase
        .from("destinations")
        .select("*");

      if (error) {
        console.error("Error fetching data:", error);
        // Re-added toast notification for user feedback
        toast.error("Failed to load destinations data");
      } else {
        setDestinations(data);
      }
    };

    fetchDestinations();
  }, []);

  // Load favorites from localStorage
  useEffect(() => {
    const savedFavorites = localStorage.getItem("uttarakhand-favorites");
    if (savedFavorites) {
      setFavorites(JSON.parse(savedFavorites));
    }
  }, []);

  // Save favorites to localStorage
  const toggleFavorite = (id: number) => {
    const newFavorites = favorites.includes(id)
      ? favorites.filter((fav) => fav !== id)
      : [...favorites, id];
    
    setFavorites(newFavorites);
    localStorage.setItem("uttarakhand-favorites", JSON.stringify(newFavorites));
    
    toast.success(
      favorites.includes(id) ? "Removed from favorites" : "Added to favorites"
    );
  };

  // Filter and sort destinations
  const filteredDestinations = useMemo(() => {
    let filtered = destinations;

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(
        (dest) =>
          dest.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          dest.district.toLowerCase().includes(searchQuery.toLowerCase()) ||
          dest.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
          dest.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Filter by category
    if (selectedCategory !== "All") {
      filtered = filtered.filter((dest) => dest.category === selectedCategory);
    }

    // Filter by favorites
    if (showFavoritesOnly) {
      filtered = filtered.filter((dest) => favorites.includes(dest.id));
    }

    // Sort
    filtered = [...filtered].sort((a, b) => {
      if (sortBy === "rating") {
        return b.rating - a.rating;
      } else if (sortBy === "district") {
        return a.district.localeCompare(b.district);
      }
      return a.name.localeCompare(b.name);
    });

    return filtered;
  }, [destinations, searchQuery, selectedCategory, sortBy, showFavoritesOnly, favorites]);

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative h-[70vh] flex items-center justify-center overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center"
          // Fixed: Added backticks (`) for template literal
          style={{ backgroundImage: `url(${heroImage})` }} 
        />
        <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-black/30 to-background" />
        
        <div className="relative z-10 text-center space-y-6 px-4 max-w-4xl mx-auto">
          <h1 className="text-5xl md:text-7xl font-bold text-white animate-fade-in drop-shadow-2xl">
            Explore Uttarakhand
          </h1>
          <p className="text-xl md:text-2xl text-white/90 animate-fade-in drop-shadow-lg">
            Discover the Divine Beauty of the Land of Gods
          </p>
          <div className="animate-fade-in pt-4">
            <SearchBar
              value={searchQuery}
              onChange={setSearchQuery}
              placeholder="Search destinations, districts, categories..."
            />
          </div>
        </div>
      </section>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12 space-y-8">
        {/* Filters and Controls */}
        <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
          <FilterControls
            selectedCategory={selectedCategory}
            onCategoryChange={setSelectedCategory}
            sortBy={sortBy}
            onSortChange={setSortBy}
          />
          
          <Button
            variant={showFavoritesOnly ? "default" : "outline"}
            onClick={() => setShowFavoritesOnly(!showFavoritesOnly)}
            className="gap-2"
          >
            <Heart className={showFavoritesOnly ? "fill-current" : ""} />
            Favorites ({favorites.length})
          </Button>
        </div>

        {/* Results Count */}
        <div className="text-center text-muted-foreground">
          Showing {filteredDestinations.length} destination
          {filteredDestinations.length !== 1 ? "s" : ""}
        </div>

        {/* Tabs for Grid and Map View */}
        <Tabs defaultValue="grid" className="w-full">
          <TabsList className="grid w-full max-w-md mx-auto grid-cols-2">
            <TabsTrigger value="grid" className="gap-2">
              <Grid className="h-4 w-4" />
              Grid View
            </TabsTrigger>
            <TabsTrigger value="map" className="gap-2">
              <Map className="h-4 w-4" />
              Map View
            </TabsTrigger>
          </TabsList>

          <TabsContent value="grid" className="mt-8">
            {filteredDestinations.length === 0 ? (
              <div className="text-center py-20">
                <p className="text-2xl text-muted-foreground">
                  No destinations found
                </p>
                <p className="text-sm text-muted-foreground mt-2">
                  Try adjusting your filters or search query
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredDestinations.map((destination, index) => (
                  <div
                    key={destination.id}
                    // Fixed: Added backticks (`) for template literal
                    style={{ animationDelay: `${index * 0.1}s` }}
                    className="animate-fade-in-up" // Assuming you have this animation
                  >
                    <DestinationCard
                      destination={destination}
                      isFavorite={favorites.includes(destination.id)}
                      onToggleFavorite={toggleFavorite}
                      onClick={() => setSelectedDestination(destination)}
                    />
                  </div>
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="map" className="mt-8">
            <MapView
              destinations={filteredDestinations}
              onMarkerClick={setSelectedDestination}
            />
          </TabsContent>
        </Tabs>
      </main>

      {/* Modal */}
      <DestinationModal
        destination={selectedDestination}
        isOpen={!!selectedDestination}
        onClose={() => setSelectedDestination(null)}
      />

      {/* Footer */}
      <footer className="bg-muted mt-20 py-8">
        <div className="container mx-auto px-4 text-center text-muted-foreground">
          <p>© 2025 Uttarakhand Tourism Explorer. Discover the Land of Gods.</p>
        </div>
      </footer>
    </div>
  );
};

export default Index;