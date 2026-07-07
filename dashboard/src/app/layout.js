export const metadata = {
    title: "Tactical SIGINT Station",
    description: "Visual Logging System"
};

export default function RootLayout({ children }) {
    return (
        <html lang="en">
            <head>
                {/* Menyuntikkan mesin desainer Tailwind CSS langsung ke browser */}
                <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body>{children}</body>
        </html>
    );
}
