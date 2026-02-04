import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Polyline, Rectangle, Polygon, Tooltip, useMap } from 'react-leaflet'
import { renderToStaticMarkup } from 'react-dom/server'
import 'leaflet/dist/leaflet.css'
import { Upload, Search, Map as MapIcon, Info, Database, Layers, Leaf, Droplets, Mountain, Ship, Zap, Pickaxe, Train, Car, Waves, MapPin, Trees, Apple, Anchor, Factory, Sun, Flame, Menu, X, ChevronRight, Fuel, CloudRain, Users, Plane, Milestone, ArrowLeft } from 'lucide-react'
import type { LatLngExpression } from 'leaflet'
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

interface GISFeature {
    type: 'region' | 'path' | 'point';
    label: string;
    data: any[];
    color: string;
    icon?: string;
    opacity?: number;
}

interface LegendItem {
    label: string;
    color: string;
    icon: string;
}

interface GeographyModuleProps {
    onBack: () => void;
}

export default function GeographyModule({ onBack }: GeographyModuleProps) {
    const [query, setQuery] = useState('')
    const [mapImage, setMapImage] = useState<string | null>(null)
    const [imageFile, setImageFile] = useState<File | null>(null)
    const [isAnalyzing, setIsAnalyzing] = useState(false)
    const [analysisResults, setAnalysisResults] = useState<{
        features: GISFeature[];
        legend: LegendItem[];
        explanation: string;
    } | null>(null)
    const [isSidebarOpen, setIsSidebarOpen] = useState(true)

    const categories = [
        { label: "Provinces", icon: <MapIcon size={14} />, query: "provinces and administrative divisions" },
        { label: "Physical Features", icon: <Layers size={14} />, query: "plains, doabs, and deltas" },
        { label: "Climate & Rain", icon: <CloudRain size={14} />, query: "monsoon and rain systems" },
        { label: "Rivers & Barrages", icon: <Droplets size={14} />, query: "rivers and barrages in pakistan" },
        { label: "Mountain Ranges", icon: <Mountain size={14} />, query: "northern and western mountain ranges" },
        { label: "Deserts & Plateaus", icon: <Sun size={14} />, query: "deserts and plateaus of pakistan" },
        { label: "Agriculture", icon: <Leaf size={14} />, query: "wheat, rice, cotton, and oilseed regions" },
        { label: "Livestock Areas", icon: <Trees size={14} />, query: "sheep, buffalo, and goat rearing areas" },
        { label: "Mining & Resources", icon: <Pickaxe size={14} />, query: "mining methods and mineral resources" },
        { label: "Energy & Power", icon: <Zap size={14} />, query: "power plants and oil/gas fields" },
        { label: "Industries", icon: <Factory size={14} />, query: "textile, sugar, fertilizer, and cement industries" },
        { label: "Infrastructure", icon: <Train size={14} />, query: "cpec corridors, roads, and railways" },
        { label: "Airports", icon: <Plane size={14} />, query: "international and domestic airports" },
        { label: "Population", icon: <Users size={14} />, query: "population density and distribution" },
    ]

    const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (file) {
            setImageFile(file)
            const reader = new FileReader()
            reader.onload = (event) => {
                setMapImage(event.target?.result as string)
            }
            reader.readAsDataURL(file)
        }
    }

    const handleAnalyze = async () => {
        if (!query || !imageFile) {
            alert("Please upload a map and enter a query first.")
            return
        }

        setIsAnalyzing(true)
        const formData = new FormData()
        formData.append('query', query)
        formData.append('image', imageFile)

        try {
            const response = await fetch('http://localhost:8000/analyze-map', {
                method: 'POST',
                body: formData,
            })
            const data = await response.json()
            setAnalysisResults(data)
        } catch (error) {
            console.error("Error analyzing map:", error)
            alert("Failed to connect to backend. Make sure it's running.")
        } finally {
            setIsAnalyzing(false)
        }
    }

    const handleCategoryClick = (categoryQuery: string) => {
        setQuery(categoryQuery)
        setTimeout(() => {
            const analyzeWithCategory = async () => {
                if (!imageFile) {
                    alert("Please upload a map first.")
                    return
                }
                setIsAnalyzing(true)
                const formData = new FormData()
                formData.append('query', categoryQuery)
                formData.append('image', imageFile)
                try {
                    const response = await fetch('http://localhost:8000/analyze-map', {
                        method: 'POST',
                        body: formData,
                    })
                    const data = await response.json()
                    setAnalysisResults(data)
                } catch (error) {
                    console.error("Error analyzing map:", error)
                } finally {
                    setIsAnalyzing(false)
                }
            }
            analyzeWithCategory()
        }, 0)
    }

    const renderIcon = (iconName: string, size = 14, color?: string) => {
        const className = color ? "" : "text-indigo-400"
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

    const createCustomIcon = (iconName: string, color: string) => {
        const iconHtml = renderToStaticMarkup(
            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-slate-900/80 border-2 shadow-lg backdrop-blur-sm transition-transform hover:scale-110" style={{ borderColor: color }}>
                {renderIcon(iconName, 18, color)}
            </div>
        )
        return L.divIcon({
            html: iconHtml,
            className: 'custom-div-icon',
            iconSize: [32, 32],
            iconAnchor: [16, 16]
        })
    }


    function FixMapSize() {
        const map = useMap();
        useEffect(() => {
            // Initial fix after component mounts and animation might be settling
            const timer = setTimeout(() => {
                map.invalidateSize();
            }, 500);

            const handleResize = () => {
                map.invalidateSize();
            };
            window.addEventListener('resize', handleResize);
            return () => {
                window.removeEventListener('resize', handleResize);
                clearTimeout(timer);
            };
        }, [map]);
        return null;
    }

    return (
        <div className="h-full flex flex-col overflow-hidden bg-slate-950 text-slate-50 relative">
            <header className="h-16 flex-shrink-0 bg-slate-900/50 backdrop-blur-xl border-b border-white/5 px-6 flex items-center gap-4 z-[1000]">
                <button onClick={onBack} className="p-2 hover:bg-white/5 rounded-lg transition-colors flex items-center gap-2 text-slate-400 hover:text-white group">
                    <ArrowLeft size={18} className="group-hover:-translate-x-0.5 transition-transform" />
                    <span className="text-sm font-medium">Dashboard</span>
                </button>
                <div className="h-6 w-px bg-white/10 mx-2"></div>
                <div className="flex items-center gap-3 flex-1">
                    <div className="p-1.5 bg-indigo-600 rounded-lg">
                        <MapIcon size={18} className="text-white" />
                    </div>
                    <h1 className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-cyan-400">
                        Geography Module
                    </h1>
                </div>
                <button
                    onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                    className="p-2 hover:bg-white/5 rounded-lg transition-all duration-200 text-slate-400 hover:text-white flex items-center gap-2"
                    title={isSidebarOpen ? "Close Sidebar" : "Open Sidebar"}
                >
                    {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
                </button>
            </header>

            <main className="flex-1 flex flex-col lg:flex-row relative overflow-hidden">
                <section className={`absolute lg:relative z-[999] h-full flex flex-col gap-4 flex-shrink-0 overflow-y-auto custom-scrollbar transition-all duration-300 ease-in-out bg-slate-950/80 backdrop-blur-xl lg:bg-transparent ${isSidebarOpen ? 'w-[280px] p-4 border-r border-white/5 lg:border-none translate-x-0' : 'w-0 -translate-x-full lg:translate-x-0 p-0 overflow-hidden'}`}>
                    <div className="glass-panel p-4 flex flex-col gap-3">
                        <h2 className="text-xs font-bold uppercase tracking-widest text-slate-500">1. Upload Base Map</h2>
                        <div className={`group border-2 border-dashed ${mapImage ? 'border-indigo-500/50 bg-indigo-500/5' : 'border-white/10'} rounded-xl p-6 flex flex-col items-center justify-center gap-2 cursor-pointer hover:border-indigo-400/50 hover:bg-white/5 transition-all duration-300 relative`}>
                            <input type="file" className="absolute inset-0 opacity-0 cursor-pointer" onChange={handleImageUpload} accept="image/*" />
                            {mapImage ? (
                                <div className="w-full text-center">
                                    <div className="w-full h-24 mb-2 rounded-lg overflow-hidden border border-indigo-500/20 shadow-inner">
                                        <img src={mapImage} alt="Preview" className="w-full h-full object-cover" />
                                    </div>
                                    <p className="text-[10px] text-indigo-300 font-semibold italic">Map Loaded • Click to Replace</p>
                                </div>
                            ) : (
                                <>
                                    <Upload size={32} className="text-slate-500 group-hover:text-indigo-400 transition-colors" />
                                    <p className="text-xs font-medium text-slate-400 text-center">Drop high-res Pakistan map</p>
                                </>
                            )}
                        </div>
                    </div>

                    <div className="glass-panel p-4 flex flex-col gap-3">
                        <h2 className="text-xs font-bold uppercase tracking-widest text-slate-500">2. Custom Query</h2>
                        <div className="relative group">
                            <input type="text" placeholder="e.g. Find rice growing regions" className="w-full bg-slate-900/50 border border-white/10 rounded-xl py-2.5 pl-9 pr-4 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all shadow-inner placeholder:text-slate-600" value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()} />
                            <Search className="absolute left-3 top-3 text-slate-500" size={14} />
                        </div>
                        <button className="w-full bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold py-2.5 rounded-xl transition-all shadow-lg shadow-indigo-600/20 active:scale-[0.97] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2" onClick={handleAnalyze} disabled={isAnalyzing || !imageFile}>
                            {isAnalyzing ? "Analyzing..." : "Analyze Custom Query"}
                        </button>
                    </div>

                    <div className="glass-panel p-4 flex flex-col min-h-0 overflow-hidden">
                        <h2 className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-3 flex items-center gap-2">
                            <Layers size={14} className="text-indigo-400" /> Explore Layers
                        </h2>
                        <div className="flex-1 overflow-y-auto pr-1 space-y-1.5 custom-scrollbar pb-2">
                            {categories.map((cat, idx) => (
                                <button key={idx} onClick={() => handleCategoryClick(cat.query)} className="w-full flex items-center gap-3 p-2 bg-white/5 rounded-lg border border-white/5 hover:bg-indigo-600/20 hover:border-indigo-500/30 transition-all text-left group">
                                    <div className="w-7 h-7 rounded-md bg-slate-900 flex items-center justify-center shrink-0 border border-white/10 group-hover:border-indigo-500/50 group-hover:bg-indigo-600 transition-all">
                                        {cat.icon}
                                    </div>
                                    <span className="text-[11px] font-bold text-slate-300 group-hover:text-white">{cat.label}</span>
                                    <ChevronRight size={12} className="ml-auto text-slate-600 group-hover:text-white" />
                                </button>
                            ))}
                        </div>
                    </div>
                </section>

                <section id="map-section-container" className="flex-1 glass-panel relative border-white/10 m-2 lg:m-4 min-h-[400px] lg:min-h-0 overflow-hidden rounded-2xl shadow-inner bg-slate-900/20">
                    {!mapImage ? (
                        <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-600 animate-pulse bg-slate-900/40 p-6 text-center">
                            <MapIcon size={80} className="mb-4 opacity-10" />
                            <p className="text-lg font-semibold tracking-tight">GIS Terminal Standby</p>
                            <p className="text-xs opacity-60">Upload base map to initialize spatial analysis</p>
                        </div>
                    ) : (
                        <div key={mapImage ? 'loaded' : 'empty'} className="w-full h-full relative">
                            <MapContainer center={[30.3753, 69.3451] as LatLngExpression} zoom={5} style={{ height: '100%', width: '100%' }} className="z-0">
                                <FixMapSize />
                                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution='&copy; OpenStreetMap contributors' />

                                {analysisResults?.features.map((feature: GISFeature, fIdx: number) => (
                                    <div key={fIdx}>
                                        {feature.type === 'region' && feature.data.map((region: any, rIdx: number) => {
                                            const isPolygon = Array.isArray(region.coordinates) && region.coordinates.length > 2;
                                            return (
                                                <div key={rIdx}>
                                                    {isPolygon ? (
                                                        <Polygon positions={region.coordinates} pathOptions={{ color: feature.color, fillColor: feature.color, fillOpacity: feature.opacity || 0.2, weight: 1.5 }}>
                                                            <Popup>
                                                                <div className="p-1">
                                                                    <h4 className="font-bold text-indigo-600">{region.name}</h4>
                                                                    <p className="text-xs">{region.description}</p>
                                                                </div>
                                                            </Popup>
                                                        </Polygon>
                                                    ) : (
                                                        <Rectangle bounds={region.coordinates} pathOptions={{ color: feature.color, fillColor: feature.color, fillOpacity: feature.opacity || 0.2, weight: 1.5 }}>
                                                            <Popup>
                                                                <div className="p-1">
                                                                    <h4 className="font-bold text-indigo-600">{region.name}</h4>
                                                                    <p className="text-xs">{region.description}</p>
                                                                </div>
                                                            </Popup>
                                                        </Rectangle>
                                                    )}
                                                </div>
                                            );
                                        })}
                                        {feature.type === 'path' && (
                                            <Polyline positions={feature.data} pathOptions={{ color: feature.color, weight: 3, opacity: 0.7 }}>
                                                <Tooltip permanent direction="center" className="river-label">
                                                    <span className="text-[11px] font-extrabold text-black uppercase tracking-wider">{feature.label}</span>
                                                </Tooltip>
                                                <Popup>
                                                    <div className="p-1">
                                                        <h4 className="font-bold whitespace-nowrap" style={{ color: feature.color }}>{feature.label}</h4>
                                                        <p className="text-xs">{feature.data[0]?.facts || feature.label}</p>
                                                    </div>
                                                </Popup>
                                            </Polyline>
                                        )}
                                        {feature.type === 'point' && feature.data.map((coord: any, pIdx: number) => (
                                            <Marker key={pIdx} position={coord} icon={feature.icon ? createCustomIcon(feature.icon, feature.color) : undefined}>
                                                <Popup>
                                                    <div className="p-1">
                                                        <h4 className="font-bold" style={{ color: feature.color }}>{feature.label}</h4>
                                                        {feature.data[pIdx]?.facts && <p className="text-xs mt-1">{feature.data[pIdx].facts}</p>}
                                                    </div>
                                                </Popup>
                                            </Marker>
                                        ))}
                                    </div>
                                ))}
                            </MapContainer>
                        </div>
                    )}

                    {isAnalyzing && (
                        <div className="absolute inset-0 z-10 bg-slate-950/80 backdrop-blur-md flex items-center justify-center transition-all duration-500">
                            <div className="flex flex-col items-center gap-6">
                                <div className="relative">
                                    <div className="w-16 h-16 border-4 border-indigo-500/20 rounded-full animate-ping"></div>
                                    <div className="absolute inset-0 w-16 h-16 border-t-4 border-indigo-500 rounded-full animate-spin"></div>
                                </div>
                                <div className="text-center">
                                    <p className="text-xl font-black text-white tracking-[0.2em] uppercase mb-2">Analyzing Geometry</p>
                                    <p className="text-xs text-indigo-400 font-mono animate-pulse">Scanning map alignments | Fetching PBS Datasets</p>
                                </div>
                            </div>
                        </div>
                    )}
                </section>

                <section id="insights-panel-container" className="w-full lg:w-80 flex-shrink-0 glass-panel p-6 flex flex-col gap-6 border-white/10 bg-slate-900/60 shadow-2xl overflow-hidden m-4 rounded-2xl">
                    <h2 className="text-xs font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2 border-b border-white/5 pb-4">
                        <Info size={14} className="text-cyan-400" /> Geography Insights
                    </h2>
                    <div className="flex-1 overflow-y-auto pr-3 text-[14px] leading-relaxed text-slate-300 custom-scrollbar scroll-smooth break-words">
                        {analysisResults?.explanation ? (
                            <div className="animate-in fade-in slide-in-from-bottom-2 duration-500 whitespace-pre-wrap break-words overflow-x-hidden">
                                {analysisResults.explanation.split('\n').map((line: string, i: number) => {
                                    if (line.startsWith('###')) return <h3 key={i} className="text-lg font-bold text-white mt-4 mb-2">{line.replace('###', '')}</h3>
                                    if (line.startsWith('- **')) {
                                        const [label, ...val] = line.replace('- **', '').split('**: ')
                                        return <p key={i} className="mb-2"><strong className="text-indigo-400">{label}:</strong> {val.join('**: ')}</p>
                                    }
                                    if (line.includes('**')) {
                                        return <p key={i} className="mb-2">
                                            {line.split('**').map((part: string, j: number) => j % 2 === 1 ? <strong key={j} className="text-indigo-400">{part}</strong> : part)}
                                        </p>
                                    }
                                    return line ? <p key={i} className="mb-2">{line}</p> : <br key={i} />
                                })}
                            </div>
                        ) : (
                            <div className="space-y-4">
                                <p className="text-slate-400 italic text-xs">Execute a search to retrieve curriculum-aligned geographic facts.</p>
                                <div className="p-4 bg-indigo-500/5 rounded-2xl border border-indigo-500/10">
                                    <h3 className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-2 flex items-center gap-1">
                                        <Database size={12} /> Live Fact
                                    </h3>
                                    <p className="text-xs leading-relaxed text-indigo-300/80">Pakistan's topography is divided into three main regions: Northern Highlands, Indus River Plain, and Balochistan Plateau.</p>
                                </div>
                            </div>
                        )}
                    </div>
                </section>
            </main>
        </div>
    )
}
