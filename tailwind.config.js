/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html', // Todas las plantillas HTML de Django
    './**/templates/**/*.html', // Plantillas en subdirectorios de apps Django
    './static/**/*.js', // Archivos JS en la carpeta static
    './static/**/*.css', // Archivos CSS en la carpeta static (opcional si usas Tailwind directamente en JS)
  ],
  theme: {
    extend: {
      colors: {
        // Ejemplo de personalización de colores
        primary: '#1d4ed8',
        secondary: '#9333ea',
        accent: '#fbbf24',
        dark: '#1e293b',
        cancelGray: '#6b7280', 
        cancelHover: '#4b5563', 
      fontFamily: {
        // Ejemplo de personalización de fuentes
        sans: ['Inter', 'sans-serif'],
        serif: ['Merriweather', 'serif'],
      },
      spacing: {
        // Ejemplo de personalización de espaciados
        '128': '32rem',
        '144': '36rem',
      },
      
    },
  },
  plugins: [
    require('@tailwindcss/forms'), // Mejora los estilos de formularios
    require('@tailwindcss/typography'), // Añade estilos para contenido rico en texto
    require('@tailwindcss/aspect-ratio'), // Manejo de relaciones de aspecto
  ],
};
