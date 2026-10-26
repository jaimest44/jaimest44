# Modelo 3D de la vivienda (Villa de Otura)

- `visor-3d.html`: el visor interactivo publicado en https://claude.ai/artifact/VNp8WMrejyhjnkFGMzp5mV
  (cortes por planta, jardín a −0,95 / −1,80, avance de obra, sol y sombras).
  Es un fragmento de página: para abrirlo en local, sírvelo con un servidor estático
  (por ejemplo `npx serve .`) y ábrelo en el navegador; carga three.js desde cdn.jsdelivr.net.
- `video-escena.html`: escena usada para los vídeos de la obra. `?g=-1.80` activa la variante.
- `render.js`: renderiza el vídeo con Playwright + ffmpeg.
  Necesita `npm i three@0.160.0 playwright-core` y copiar `video-escena.html` como `index.html` junto a `node_modules`.
  Uso: `node render.js full salida.mp4` (con `Q='?g=-1.80'` para la variante).
- `compare.js`: genera las imágenes comparativas a la altura de los ojos.
- `tour.js`: renderiza el vídeo del recorrido (house tour) a partir de `visor-3d.html`, que incluye la ruta de cámara (`window.tourAt`).
  Uso: `node tour.js full salida.mp4` (o `node tour.js test 10,20,30` para sacar fotogramas sueltos).

Las medidas salen de los planos del proyecto básico; tabiques, alzados sin cota, materiales y entorno son aproximados.
