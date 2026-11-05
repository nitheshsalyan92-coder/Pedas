import { useEffect, useRef } from "react";
import L from "leaflet";

const COLORS = {
  High: "#e11d48",
  Medium: "#d97706",
  Low: "#059669",
};

export default function RiskMap({ zones, selectedId, onSelect }) {
  const containerRef = useRef(null);
  const mapRef = useRef(null);
  const layerRef = useRef(null);
  const onSelectRef = useRef(onSelect);

  useEffect(() => {
    onSelectRef.current = onSelect;
  }, [onSelect]);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return undefined;

    const map = L.map(containerRef.current, { scrollWheelZoom: true }).setView([12.975, 77.6], 13);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(map);
    layerRef.current = L.layerGroup().addTo(map);
    mapRef.current = map;
    const timer = setTimeout(() => map.invalidateSize(), 150);

    return () => {
      clearTimeout(timer);
      map.remove();
      mapRef.current = null;
      layerRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    const layer = layerRef.current;
    if (!map || !layer) return;
    layer.clearLayers();

    zones.forEach((zone) => {
      const selected = zone.id === selectedId;
      const marker = L.circleMarker([zone.lat, zone.lng], {
        radius: selected ? 14 : 9,
        color: "#ffffff",
        weight: selected ? 3 : 2,
        fillColor: COLORS[zone.level],
        fillOpacity: 0.92,
      });
      marker.bindTooltip(`${zone.name} · ${zone.level} · ${zone.riskPercent}%`);
      marker.on("click", () => onSelectRef.current(zone.id));
      marker.addTo(layer);
    });

    if (zones.length) {
      map.fitBounds(L.latLngBounds(zones.map((zone) => [zone.lat, zone.lng])).pad(0.35));
    }
  }, [zones, selectedId]);

  return <div ref={containerRef} className="h-[480px] w-full" />;
}
