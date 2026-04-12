import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Polyline, Rectangle, Polygon, Tooltip, useMap } from 'react-leaflet'
import { renderToStaticMarkup } from 'react-dom/server'
import 'leaflet/dist/leaflet.css'
import { Upload, Search, Map as MapIcon, Info, Database, Layers, Leaf, Droplets, Mountain, Ship, Zap, Pickaxe, Train, Car, Waves, MapPin, Trees, Apple, Anchor, Factory, Sun, Flame, Menu, X, ChevronRight, Fuel, CloudRain, Users, Plane, Milestone, ArrowLeft, ChevronLeft, Sparkles, Brain } from 'lucide-react'
import L from 'leaflet'
import icon from 'leaflet/dist/images/marker-icon.png'
import iconShadow from 'leaflet/dist/images/marker-shadow.png'

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

export default function GeographyModule({ onBack }) {

    const [query, setQuery] = useState('')
    const [mapImage, setMapImage] = useState(null)
    const [imageFile, setImageFile] = useState(null)
    const [isAnalyzing, setIsAnalyzing] = useState(false)
    const [analysisResults, setAnalysisResults] = useState(null)
    const [isSidebarOpen, setIsSidebarOpen] = useState(true)

    const categories = [
        { label: "Provinces", icon: <MapIcon size={14} />, query: "provinces and administrative divisions" },
        { label: "Physical Features", icon: <Layers size={14} />, query: "plains, doabs, and deltas" },
        { label: "Climate & Rain", icon: <CloudRain size={14} />, query: "monsoon and rain systems" },
        { label: "Rivers & Barrages", icon: <Droplets size={14} />, query: "rivers and barrages in Pakistan" },
        { label: "Mountain Ranges", icon: <Mountain size={14} />, query: "mountain ranges and major peaks" },
        { label: "Canals & Irrigation", icon: <Waves size={14} />, query: "canals and irrigation systems" },
        { label: "Glaciers & Passes", icon: <Ship size={14} />, query: "glaciers and mountain passes" },
        { label: "Deserts & Plateaus", icon: <Sun size={14} />, query: "deserts and plateaus of Pakistan" },
        { label: "Agriculture", icon: <Leaf size={14} />, query: "wheat, rice, cotton, and oilseed regions" },
        { label: "Livestock Areas", icon: <Trees size={14} />, query: "sheep, buffalo, and goat rearing areas" },
        { label: "Mining & Resources", icon: <Pickaxe size={14} />, query: "mining methods and mineral resources" },
        { label: "Energy & Refineries", icon: <Zap size={14} />, query: "power plants and oil refineries" },
        { label: "Industries", icon: <Factory size={14} />, query: "textile, sugar, fertilizer, and cement industries" },
        { label: "Infrastructure & Grid", icon: <Train size={14} />, query: "roads, railways, and grid system" },
        { label: "Airports & Ports", icon: <Plane size={14} />, query: "airports and seaports in Pakistan" },
        { label: "Population", icon: <Users size={14} />, query: "population density and distribution" },
    ]

    const handleImageUpload = (e) => {
        const file = e.target.files?.[0]
        if (file) {
            setImageFile(file)
            const reader = new FileReader()
            reader.onload = (event) => {
                setMapImage(event.target?.result)
            }
            reader.readAsDataURL(file)
        }
    }

    const handleAnalyze = async () => {
        if (!query) return
        setIsAnalyzing(true)
        const formData = new FormData()
        formData.append('query', query)
        if (imageFile) formData.append('image', imageFile)

        try {
            const response = await fetch('http://localhost:8000/geography/analyze-map', {
                method: 'POST',

                body: formData,
            })
            const data = await response.json()
            if (response.ok) {
                setAnalysisResults(data)
                if (window.innerWidth < 1024) setIsSidebarOpen(false)
            } else {
                console.error("Analysis failed:", data)
            }
        } catch (error) {
            console.error("Error analyzing map:", error)
        } finally {
            setIsAnalyzing(false)
        }
    }

    const handleCategoryClick = (categoryQuery) => {
        setQuery(categoryQuery)
        setTimeout(() => handleAnalyze(), 0)
    }

    const renderIcon = (iconName, size = 14, color) => {
        const className = color ? "" : "text-[#4d3e77]"
        const props = { size, className, style: color ? { color } : {} }

        switch (iconName) {
            case 'leaf': return <Leaf {...props} />
            case 'droplets': return <Droplets {...props} />
            case 'mountain': return <Mountain {...props} />
            case 'ship': return <Ship {...props} />
            case 'anchor': return <Anchor {...props} />
            case 'zap': return <Zap {...props} />
            case 'pickaxe': return <Pickaxe {...props} />
            case 'train': return <Train {...props} />
            case 'car': return <Car {...props} />
            case 'waves': return <Waves {...props} />
            case 'map-pin': return <MapPin {...props} />
            case 'tree': return <Trees {...props} />
            case 'apple': return <Apple {...props} />
            case 'factory': return <Factory {...props} />
            case 'sun': return <Sun {...props} />
            case 'flame': return <Flame {...props} />
            case 'fuel': return <Fuel {...props} />
            case 'cloud-rain': return <CloudRain {...props} />
            case 'users': return <Users {...props} />
            case 'plane': return <Plane {...props} />
            case 'cow': return <Trees {...props} />
            case 'milestone': return <Milestone {...props} />
            default: return <Layers {...props} />
        }
    }

    const createCustomIcon = (iconName, color) => {
        const iconHtml = renderToStaticMarkup(
            <div className="flex items-center justify-center w-10 h-10 rounded-2xl bg-white border-2 shadow-2xl transition-transform hover:scale-110" style={{ borderColor: color || '#4d3e77' }}>
                {renderIcon(iconName, 22, color)}
            </div>
        )
        return L.divIcon({
            html: iconHtml,
            className: 'custom-div-icon',
            iconSize: [40, 40],
            iconAnchor: [20, 20]
        })
    }

    function FixMapSize() {
        const map = useMap();
        useEffect(() => {
            const timer = setTimeout(() => {
                map.invalidateSize();
            }, 500);
            const handleResize = () => map.invalidateSize();
            window.addEventListener('resize', handleResize);
            return () => {
                window.removeEventListener('resize', handleResize);
                clearTimeout(timer);
            };
        }, [map]);
        return null;
    }

    return (
        <div className="h-full flex flex-col overflow-hidden bg-[var(--bg-cream)] text-[var(--text-dark)] relative font-medium transition-colors duration-500">
            <header className="h-20 flex-shrink-0 bg-[var(--bg-card)]/70 backdrop-blur-xl border-b border-[var(--border-color)] px-6 flex items-center justify-between z-[1001] sticky top-0 transition-colors duration-500">
                <div className="flex items-center gap-4">
                    <button onClick={onBack} className="p-2 hover:bg-[var(--primary-purple-light)]/10 rounded-xl transition-colors text-[var(--primary-purple)] group">
                        <ChevronLeft size={24} className="group-hover:-translate-x-1 transition-transform" />
                    </button>
                    <div className="h-8 w-[1px] bg-[var(--border-color)] mx-1"></div>
                    <div>
                        <h2 className="text-xl font-black text-[var(--primary-purple)] flex items-center gap-2">
                            GIS Analyst
                        </h2>
                        <p className="text-[10px] font-black uppercase tracking-widest text-[var(--accent-gold)]">Spatial Intelligence Hub</p>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <button
                        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                        className="p-3 bg-[var(--bg-card)] border border-[var(--border-color)] hover:bg-[var(--primary-purple-light)]/10 rounded-xl transition-all shadow-sm text-[var(--primary-purple)]"
                    >
                        {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
                    </button>
                </div>
            </header>

            <main className="flex-1 flex flex-col lg:flex-row relative overflow-hidden">
                {/* Sidebar Drawer */}
                <aside className={`fixed lg:relative z-[1000] h-[calc(100%-5rem)] lg:h-full flex flex-col gap-6 flex-shrink-0 overflow-y-auto custom-scrollbar transition-all duration-500 ease-in-out bg-[var(--bg-card)]/80 backdrop-blur-2xl border-r border-[var(--border-color)] shadow-2xl lg:shadow-none ${isSidebarOpen ? 'w-full sm:w-[380px] p-6 translate-x-0' : 'w-0 -translate-x-full lg:translate-x-0 lg:w-0 p-0 overflow-hidden opacity-0'}`}>

                    {/* Upload Section */}
                    <div className="bg-[var(--bg-card)] rounded-[2rem] border border-[var(--border-color)] p-6 space-y-4 shadow-xl shadow-purple-900/5 dark:shadow-black/20">
                        <div className="flex items-center gap-3">
                            <Upload size={16} className="text-[var(--accent-gold)]" />
                            <h2 className="text-[10px] font-black uppercase tracking-widest text-[var(--text-muted)]">Syllabus Map Context</h2>
                        </div>
                        <div className={`group relative border-2 border-dashed ${mapImage ? 'border-[var(--primary-purple)] bg-[var(--primary-purple-light)]/5' : 'border-[var(--border-color)]'} rounded-3xl p-6 flex flex-col items-center justify-center gap-4 cursor-pointer hover:border-[var(--primary-purple)] hover:bg-[var(--primary-purple-light)]/10 transition-all duration-300`}>
                            <input type="file" className="absolute inset-0 opacity-0 cursor-pointer" onChange={handleImageUpload} accept="image/*" />
                            {mapImage ? (
                                <div className="w-full text-center">
                                    <img src={mapImage} alt="Preview" className="w-full h-24 object-cover rounded-2xl mb-3 shadow-lg" />
                                    <p className="text-[10px] text-[var(--primary-purple)] font-black uppercase tracking-widest">Replace Analysis Image</p>
                                </div>
                            ) : (
                                <>
                                    <div className="w-12 h-12 rounded-2xl bg-[var(--primary-purple-light)]/10 flex items-center justify-center text-[var(--primary-purple)] group-hover:scale-110 transition-transform">
                                        <Upload size={20} />
                                    </div>
                                    <p className="text-[10px] font-black text-[var(--text-muted)] text-center uppercase tracking-widest">Upload Exam Reference Map</p>
                                </>
                            )}
                        </div>
                    </div>

                    {/* Query Section */}
                    <div className="bg-[var(--primary-purple)] rounded-[2rem] p-6 space-y-4 shadow-xl shadow-purple-900/20 dark:shadow-black/40">
                        <div className="flex items-center gap-3">
                            <Search size={16} className="text-white" />
                            <h2 className="text-[10px] font-black uppercase tracking-widest text-white opacity-60">GIS Terminal Query</h2>
                        </div>
                        <div className="relative">
                            <input
                                type="text"
                                placeholder="e.g. Find Indus River System"
                                className="w-full bg-white/10 dark:bg-black/20 border border-white/20 dark:border-white/10 rounded-2xl py-4 pl-12 pr-4 text-sm text-white placeholder:text-white/40 focus:ring-4 focus:ring-white/5 outline-none transition-all"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
                            />
                            <Search className="absolute left-4 top-4.5 text-white/60" size={18} />
                        </div>
                        <button
                            className="w-full bg-white text-[var(--primary-purple)] text-[10px] font-black uppercase tracking-[0.2em] py-4 rounded-2xl transition-all shadow-xl hover:scale-[1.02] active:scale-95 disabled:opacity-20"
                            onClick={handleAnalyze}
                            disabled={isAnalyzing || !query}
                        >
                            {isAnalyzing ? "Processing Data..." : "Run Spatial Diagnostic"}
                        </button>
                    </div>

                    {/* Layers Section */}
                    <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
                        <div className="flex items-center justify-between px-2 mb-4">
                            <div className="flex items-center gap-3">
                                <Layers size={16} className="text-[var(--accent-gold)]" />
                                <h2 className="text-[10px] font-black uppercase tracking-widest text-[var(--text-muted)]">Interactive Syllabus Layers</h2>
                            </div>
                        </div>
                        <div className="flex-1 overflow-y-auto pr-1 space-y-2 custom-scrollbar pb-6 text-[var(--text-dark)]">
                            {categories.map((cat, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => handleCategoryClick(cat.query)}
                                    className="w-full flex items-center gap-4 p-3 bg-[var(--bg-card)] rounded-2xl border border-[var(--border-color)] hover:border-[var(--primary-purple)] hover:shadow-xl hover:shadow-purple-900/5 dark:hover:shadow-black/20 transition-all text-left group"
                                >
                                    <div className="w-10 h-10 rounded-xl bg-[var(--primary-purple-light)]/10 flex items-center justify-center shrink-0 group-hover:bg-[var(--primary-purple)] group-hover:text-white transition-all text-[var(--primary-purple)]">
                                        {cat.icon}
                                    </div>
                                    <span className="text-xs font-black text-[var(--text-muted)] uppercase tracking-widest group-hover:text-[var(--primary-purple)]">{cat.label}</span>
                                    <ChevronRight size={14} className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity text-[var(--accent-gold)]" />
                                </button>
                            ))}
                        </div>
                    </div>
                </aside>

                <section className="flex-1 flex flex-col min-w-0 bg-[var(--bg-cream)] overflow-hidden transition-colors duration-500">
                    <div id="map-section-container" className="flex-1 relative mx-4 mb-4 lg:mx-8 lg:mb-8 rounded-[3rem] overflow-hidden border border-[var(--border-color)] bg-[var(--bg-card)] shadow-2xl shadow-purple-900/10 dark:shadow-black/40 min-h-[500px] lg:min-h-0">
                        <MapContainer center={[30.3753, 69.3451]} zoom={5} style={{ height: '100%', width: '100%' }} className="z-0">
                            <FixMapSize />
                            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution='&copy; OpenStreetMap contributors' />

                            {analysisResults?.features?.sort((a, b) => {
                                const order = { 'region': 1, 'path': 2, 'point': 3 };
                                return (order[a.type] || 0) - (order[b.type] || 0);
                            }).map((feature, fIdx) => {
                                if (!feature || !feature.data) return null;
                                return (
                                    <div key={fIdx}>
                                        {feature.type === 'region' && feature.data?.map((region, rIdx) => {
                                            if (!region || !region.coordinates) return null;
                                            const isPolygon = Array.isArray(region.coordinates) && region.coordinates.length > 2;
                                            return (
                                                <div key={rIdx}>
                                                    {isPolygon ? (
                                                        <Polygon positions={region.coordinates} pathOptions={{ color: feature.color, fillColor: feature.color, fillOpacity: feature.opacity || 0.2, weight: 2.5 }}>
                                                            <Popup className="academic-popup">
                                                                <div className="p-2 min-w-[150px] bg-[var(--bg-card)] text-[var(--text-dark)]">
                                                                    <h4 className="font-black text-[var(--primary-purple)] uppercase tracking-widest text-xs border-b border-[var(--border-color)] pb-2 mb-2">{region.name}</h4>
                                                                    <p className="text-[11px] leading-relaxed text-[var(--text-muted)]">{region.description}</p>
                                                                </div>
                                                            </Popup>
                                                        </Polygon>
                                                    ) : (
                                                        <Rectangle bounds={region.coordinates} pathOptions={{ color: feature.color, fillColor: feature.color, fillOpacity: feature.opacity || 0.2, weight: 2.5 }}>
                                                            <Popup className="academic-popup">
                                                                <div className="p-2 min-w-[150px] bg-[var(--bg-card)] text-[var(--text-dark)]">
                                                                    <h4 className="font-black text-[var(--primary-purple)] uppercase tracking-widest text-xs border-b border-[var(--border-color)] pb-2 mb-2">{region.name}</h4>
                                                                    <p className="text-[11px] leading-relaxed text-[var(--text-muted)]">{region.description}</p>
                                                                </div>
                                                            </Popup>
                                                        </Rectangle>
                                                    )}
                                                </div>
                                            );
                                        })}
                                        {feature.type === 'path' && (
                                            <Polyline positions={feature.data} pathOptions={{ color: feature.color || "var(--primary-purple)", weight: 6, opacity: 0.6 }}>
                                                <Tooltip permanent direction="center" className="river-label-modern">
                                                    <span className="text-[9px] font-black text-[var(--primary-purple)] uppercase tracking-[0.2em] bg-[var(--bg-card)]/90 backdrop-blur px-3 py-1 rounded-full border border-[var(--border-color)] shadow-sm">{feature.label}</span>
                                                </Tooltip>
                                                <Popup className="academic-popup">
                                                    <div className="p-2 min-w-[180px] bg-[var(--bg-card)] text-[var(--text-dark)]">
                                                        <div className="flex items-center gap-2 mb-2">
                                                            <div className="w-1.5 h-6 rounded-full" style={{ backgroundColor: feature.color }}></div>
                                                            <h4 className="font-black text-[var(--primary-purple)] uppercase tracking-tighter">{feature.label}</h4>
                                                        </div>
                                                        <p className="text-[11px] leading-relaxed text-[var(--text-muted)]">{feature.facts || feature.label}</p>
                                                    </div>
                                                </Popup>
                                            </Polyline>
                                        )}
                                        {feature.type === 'point' && feature.data?.map((coord, pIdx) => {
                                            if (!coord || !Array.isArray(coord) || coord.length < 2) return null;
                                            return (
                                                <Marker key={pIdx} position={coord} icon={feature.icon ? createCustomIcon(feature.icon, feature.color) : undefined}>
                                                    <Popup className="academic-popup">
                                                        <div className="p-2 min-w-[180px] bg-[var(--bg-card)] text-[var(--text-dark)]">
                                                            <div className="flex items-center gap-3 mb-2">
                                                                <div className="w-8 h-8 rounded-lg bg-[var(--primary-purple-light)]/10 flex items-center justify-center text-[var(--primary-purple)]">
                                                                    {renderIcon(feature.icon, 16, feature.color)}
                                                                </div>
                                                                <h4 className="font-black text-[var(--primary-purple)] uppercase tracking-widest text-xs">{feature.label}</h4>
                                                            </div>
                                                            {feature.facts && <p className="text-[11px] leading-relaxed text-[var(--text-muted)] mt-1">{feature.facts}</p>}
                                                        </div>
                                                    </Popup>
                                                </Marker>
                                            );
                                        })}
                                    </div>
                                );
                            })}
                        </MapContainer>

                        {isAnalyzing && (
                            <div className="absolute inset-0 z-10 bg-[var(--bg-card)]/70 backdrop-blur-xl flex items-center justify-center">
                                <div className="flex flex-col items-center gap-6">
                                    <div className="relative">
                                        <div className="w-20 h-20 border-8 border-[var(--primary-purple-light)]/20 rounded-full"></div>
                                        <div className="absolute inset-0 w-20 h-20 border-t-8 border-[var(--primary-purple)] rounded-full animate-spin"></div>
                                        <Brain className="absolute inset-0 m-auto text-[var(--accent-gold)] animate-pulse" size={32} />
                                    </div>
                                    <div className="text-center">
                                        <p className="text-sm font-black uppercase tracking-[0.3em] text-[var(--primary-purple)]">Scanning Geo-Spatial Data</p>
                                        <p className="text-[10px] font-black text-[var(--accent-gold)] uppercase mt-2">Accessing Satellite Curriculum Layers</p>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Desktop Insights Panel */}
                    <div className="hidden lg:flex w-full h-56 m-8 mt-0 bg-[var(--bg-card)] rounded-[3rem] p-10 flex-col gap-6 border border-[var(--border-color)] shadow-2xl shadow-purple-900/5 dark:shadow-black/20 overflow-hidden">
                        <div className="flex items-center justify-between border-b border-[var(--border-color)] pb-4">
                            <div className="flex items-center gap-4">
                                <div className="w-10 h-10 rounded-2xl bg-[var(--primary-purple-light)]/10 flex items-center justify-center text-[var(--primary-purple)]">
                                    <Sparkles size={20} />
                                </div>
                                <h2 className="text-lg font-black text-[var(--primary-purple)] uppercase tracking-tighter">Syllabus Insights & Mastery Analysis</h2>
                            </div>
                            <div className="px-5 py-1.5 rounded-full bg-emerald-50 dark:bg-emerald-900/10 text-emerald-600 text-[10px] font-black uppercase tracking-widest border border-emerald-100 dark:border-emerald-900/20">
                                Live Analysis Engine
                            </div>
                        </div>
                        <div className="flex-1 overflow-y-auto pr-6 text-lg leading-relaxed text-[var(--text-muted)] custom-scrollbar whitespace-pre-wrap font-medium">
                            {analysisResults?.explanation || "Upload an exam map or select a curriculum layer to initialize spatial analysis."}
                        </div>
                    </div>
                </section>

                {/* Mobile Insights Drawer */}
                <div className={`fixed lg:hidden bottom-0 left-0 right-0 z-[1001] bg-[var(--bg-card)] border-t border-[var(--border-color)] rounded-t-[3rem] p-8 transition-transform duration-500 shadow-[0_-40px_100px_rgba(0,0,0,0.2)] ${analysisResults ? 'translate-y-0' : 'translate-y-full'}`}>
                    <div className="w-16 h-1.5 bg-[var(--border-color)] rounded-full mx-auto mb-8"></div>
                    <div className="max-h-[60vh] overflow-y-auto custom-scrollbar">
                        <div className="flex items-center gap-4 mb-6">
                            <div className="w-10 h-10 rounded-2xl bg-[var(--primary-purple)] flex items-center justify-center text-white dark:text-[#0f0a1e]">
                                <Sparkles size={20} />
                            </div>
                            <h2 className="text-xl font-black text-[var(--primary-purple)] uppercase tracking-tighter">Spatial Analysis</h2>
                        </div>
                        <div className="text-lg leading-relaxed text-[var(--text-muted)] whitespace-pre-wrap font-medium pb-8">
                            {analysisResults?.explanation}
                        </div>
                    </div>
                    <button
                        onClick={() => setAnalysisResults(null)}
                        className="w-full mt-4 py-5 bg-[var(--primary-purple)] text-white dark:text-[#0f0a1e] rounded-2xl text-xs font-black uppercase tracking-[0.2em] shadow-2xl shadow-purple-900/40 dark:shadow-black/60"
                    >
                        Return to Map
                    </button>
                </div>
            </main>
        </div>
    )
}
