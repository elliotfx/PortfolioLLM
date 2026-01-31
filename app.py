"""
Application Streamlit - Portfolio LLM
Interface de chat interactive avec Terre 3D et style Glassmorphism.
"""

import streamlit as st
from agents import Runner

from src.agent import get_agent

# Configuration de la page
st.set_page_config(
    page_title="Portfolio IA",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Composant Three.js pour la Terre 3D - Monte dans le parent
EARTH_3D_COMPONENT = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
(function() {
    // Accéder au document parent (hors de l'iframe Streamlit)
    const parentDoc = window.parent.document;
    const parentWin = window.parent;
    
    // Vérifier si le conteneur existe déjà
    if (parentDoc.getElementById('earth-container-3d')) return;
    
    // Créer le conteneur dans le parent
    const container = parentDoc.createElement('div');
    container.id = 'earth-container-3d';
    container.style.cssText = 'position: fixed; top: 0; right: 0; width: 60vw; height: 100vh; z-index: 50; overflow: hidden; background: linear-gradient(135deg, #0a0a1a 0%, #0d1b2a 50%, #1b263b 100%); pointer-events: auto;';
    parentDoc.body.insertBefore(container, parentDoc.body.firstChild);
    
    // Scène
    const scene = new THREE.Scene();
    
    // Caméra - utiliser les dimensions du parent
    // Caméra positionnée pour voir la Terre à droite
    const camera = new THREE.PerspectiveCamera(55, (parentWin.innerWidth * 0.6) / parentWin.innerHeight, 0.1, 1000);
    camera.position.z = 22;
    camera.position.x = 0;
    
    // Renderer avec fond transparent - utiliser les dimensions du parent
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(parentWin.innerWidth * 0.6, parentWin.innerHeight);
    renderer.setPixelRatio(Math.min(parentWin.devicePixelRatio || 1, 2));
    renderer.domElement.style.cursor = 'grab';
    container.appendChild(renderer.domElement);
    
    // Étoiles blanches principales (couche lointaine)
    const starsGeometry1 = new THREE.BufferGeometry();
    const starsMaterial1 = new THREE.PointsMaterial({
        color: 0xffffff,
        size: 0.15,
        sizeAttenuation: true
    });
    const starsVertices1 = [];
    for (let i = 0; i < 4000; i++) {
        const x = (Math.random() - 0.5) * 2000;
        const y = (Math.random() - 0.5) * 2000;
        const z = (Math.random() - 0.5) * 2000;
        starsVertices1.push(x, y, z);
    }
    starsGeometry1.setAttribute('position', new THREE.Float32BufferAttribute(starsVertices1, 3));
    const stars1 = new THREE.Points(starsGeometry1, starsMaterial1);
    scene.add(stars1);
    
    // Étoiles bleues (couche moyenne)
    const starsGeometry2 = new THREE.BufferGeometry();
    const starsMaterial2 = new THREE.PointsMaterial({
        color: 0xaaccff,
        size: 0.18,
        sizeAttenuation: true
    });
    const starsVertices2 = [];
    for (let i = 0; i < 3000; i++) {
        const x = (Math.random() - 0.5) * 1800;
        const y = (Math.random() - 0.5) * 1800;
        const z = (Math.random() - 0.5) * 1800;
        starsVertices2.push(x, y, z);
    }
    starsGeometry2.setAttribute('position', new THREE.Float32BufferAttribute(starsVertices2, 3));
    const stars2 = new THREE.Points(starsGeometry2, starsMaterial2);
    scene.add(stars2);
    
    // Étoiles jaune-orange (couche proche)
    const starsGeometry3 = new THREE.BufferGeometry();
    const starsMaterial3 = new THREE.PointsMaterial({
        color: 0xffddaa,
        size: 0.2,
        sizeAttenuation: true
    });
    const starsVertices3 = [];
    for (let i = 0; i < 3000; i++) {
        const x = (Math.random() - 0.5) * 1500;
        const y = (Math.random() - 0.5) * 1500;
        const z = (Math.random() - 0.5) * 1500;
        starsVertices3.push(x, y, z);
    }
    starsGeometry3.setAttribute('position', new THREE.Float32BufferAttribute(starsVertices3, 3));
    const stars3 = new THREE.Points(starsGeometry3, starsMaterial3);
    scene.add(stars3);
    
    // Terre (géométrie simplifiée pour meilleures performances)
    const earthGeometry = new THREE.SphereGeometry(5, 32, 32);
    
    // Texture de la Terre (NASA Blue Marble)
    const textureLoader = new THREE.TextureLoader();
    textureLoader.crossOrigin = 'anonymous';
    
    const earthTexture = textureLoader.load('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg');
    const bumpTexture = textureLoader.load('https://unpkg.com/three-globe/example/img/earth-topology.png');
    const specularTexture = textureLoader.load('https://unpkg.com/three-globe/example/img/earth-water.png');
    
    const earthMaterial = new THREE.MeshPhongMaterial({
        map: earthTexture,
        bumpMap: bumpTexture,
        bumpScale: 0.15,
        specularMap: specularTexture,
        specular: new THREE.Color(0x444444),
        shininess: 20
    });
    
    const earth = new THREE.Mesh(earthGeometry, earthMaterial);
    scene.add(earth);
    
    // Atmosphère (glow effect - géométrie simplifiée)
    const atmosphereGeometry = new THREE.SphereGeometry(5.3, 32, 32);
    const atmosphereMaterial = new THREE.ShaderMaterial({
        vertexShader: `
            varying vec3 vNormal;
            void main() {
                vNormal = normalize(normalMatrix * normal);
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            varying vec3 vNormal;
            void main() {
                float intensity = pow(0.65 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 2.0);
                gl_FragColor = vec4(0.3, 0.6, 1.0, 1.0) * intensity;
            }
        `,
        blending: THREE.AdditiveBlending,
        side: THREE.BackSide,
        transparent: true
    });
    
    const atmosphere = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial);
    scene.add(atmosphere);
    
    // Lumières
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
    scene.add(ambientLight);
    
    const sunLight = new THREE.DirectionalLight(0xffffff, 1.3);
    sunLight.position.set(50, 30, 50);
    scene.add(sunLight);
    
    // LUNE - en orbite autour de la Terre (AGRANDIE)
    const moonGeometry = new THREE.SphereGeometry(3.2, 20, 20);
    const moonTexture = textureLoader.load('https://unpkg.com/three-globe/example/img/moon.jpg');
    const moonMaterial = new THREE.MeshPhongMaterial({
        map: moonTexture,
        shininess: 5
    });
    const moon = new THREE.Mesh(moonGeometry, moonMaterial);
    moon.position.set(18, 0, 0);  // Distance de la Terre (légèrement plus loin)
    scene.add(moon);
    
    // SOLEIL - sphère brillante au loin
    const sunGeometry = new THREE.SphereGeometry(8, 24, 24);
    const sunMaterial = new THREE.MeshBasicMaterial({
        color: 0xffdd88,
        emissive: 0xffaa00,
        emissiveIntensity: 1.5
    });
    const sun = new THREE.Mesh(sunGeometry, sunMaterial);
    sun.position.set(150, 80, 150);
    scene.add(sun);
    
    // Glow effect pour le Soleil
    const sunGlowGeometry = new THREE.SphereGeometry(10, 24, 24);
    const sunGlowMaterial = new THREE.ShaderMaterial({
        vertexShader: `
            varying vec3 vNormal;
            void main() {
                vNormal = normalize(normalMatrix * normal);
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            varying vec3 vNormal;
            void main() {
                float intensity = pow(0.8 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 2.0);
                gl_FragColor = vec4(1.0, 0.8, 0.3, 1.0) * intensity;
            }
        `,
        blending: THREE.AdditiveBlending,
        side: THREE.BackSide,
        transparent: true
    });
    const sunGlow =new THREE.Mesh(sunGlowGeometry, sunGlowMaterial);
    sunGlow.position.copy(sun.position);
    scene.add(sunGlow);
    
    // Contrôles orbitaux - sur le canvas dans le parent
    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.enableZoom = true;
    controls.minDistance = 8;
    controls.maxDistance = 40;
    controls.enablePan = false;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.4;
    
    // Animation
    function animate() {
        requestAnimationFrame(animate);
        
        // Rotation lente de la Terre
        earth.rotation.y += 0.0008;
        stars.rotation.y += 0.0001;
        
        // Orbite de la Lune autour de la Terre
        const time = Date.now() * 0.0002;
        moon.position.x = Math.cos(time) * 15;
        moon.position.z = Math.sin(time) * 15;
        moon.rotation.y += 0.0005;
        
        controls.update();
        renderer.render(scene, camera);
    }
    
    animate();
    
    // Responsive - ajuster pour la zone de droite (70% de la largeur)
    window.parent.addEventListener('resize', () => {
        camera.aspect = (window.parent.innerWidth * 0.6) / window.parent.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.parent.innerWidth * 0.6, window.parent.innerHeight);
    });
})();
</script>
"""

# CSS Glassmorphism moderne
st.markdown("""
<style>
    /* Reset et fond - UNIVERS ÉTOILÉ */
    .stApp {
        background: radial-gradient(ellipse at bottom, #1b2735 0%, #090a0f 100%) !important;
        background-attachment: fixed !important;
    }
    
    /* Fond de base pour le contenu principal */
    .stMain {
        background: transparent !important;
        position: relative;
        z-index: 5;
    }
    
    /* Cacher éléments Streamlit par défaut */
    #MainMenu, footer, header {
        visibility: hidden;
    }
    
    .block-container {
        padding: 1rem 1.5rem !important;
        max-width: 100% !important;
    }
    
    /* Appliquer le glassmorphism à la première colonne (chat) - BULLE FLOTTANTE */
    [data-testid="column"]:first-child {
        position: relative !important;
        padding: 1rem !important;
        z-index: 10;
    }
    
    /* La deuxième colonne (planète) doit laisser passer les clics mais être derrière */
    [data-testid="column"]:last-child {
        pointer-events: none !important;
        z-index: 1;
    }
    
    /* Cibler tous les conteneurs verticaux dans la première colonne */
    [data-testid="column"]:first-child > div,
    [data-testid="column"]:first-child > [data-testid="stVerticalBlock"],
    [data-testid="column"]:first-child [data-testid="stVerticalBlock"]:first-child {
        background: rgba(15, 15, 35, 0.15) !important;
        backdrop-filter: blur(30px) saturate(150%) brightness(1.1) !important;
        -webkit-backdrop-filter: blur(30px) saturate(150%) brightness(1.1) !important;
        border-radius: 32px !important;
        border: 1.5px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 
            0 30px 80px rgba(0, 0, 0, 0.5),
            0 15px 50px rgba(102, 126, 234, 0.15),
            inset 0 2px 4px rgba(255, 255, 255, 0.2),
            inset 0 -2px 4px rgba(0, 0, 0, 0.2) !important;
        padding: 1.5rem 1.2rem !important;
        margin: 0 !important;
        max-height: 92vh !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
    }
    
    /* Titre avec gradient */
    .main-title {
        font-size: 1.6rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.3rem;
        padding-top: 0;
    }
    
    .subtitle {
        color: rgba(255, 255, 255, 0.6);
        text-align: center;
        font-size: 0.85rem;
        margin-bottom: 1rem;
        font-weight: 300;
    }
    
    /* Messages du chat */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.04) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        padding: 0.75rem !important;
        margin: 0.35rem 0 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stChatMessage [data-testid="stMarkdownContainer"] {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 0.85rem !important;
        line-height: 1.5 !important;
    }
    
    /* Input chat */
    .stChatInput > div {
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(102, 126, 234, 0.35) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
    }
    
    .stChatInput input {
        color: white !important;
        font-size: 0.9rem !important;
    }
    
    .stChatInput input::placeholder {
        color: rgba(255, 255, 255, 0.4) !important;
    }
    
    /* Boutons questions - REDESIGN PREMIUM */
    .stButton > button {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.03) 100%) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 16px !important;
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 0.85rem !important;
        font-weight: 400 !important;
        padding: 0.75rem 1rem !important;
        margin: 0.35rem 0 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-align: left !important;
        white-space: normal !important;
        line-height: 1.5 !important;
        height: auto !important;
        min-height: auto !important;
        width: 100% !important;
        display: block !important;
        box-shadow: 
            0 4px 12px rgba(0, 0, 0, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(145deg, rgba(102, 126, 234, 0.2) 0%, rgba(102, 126, 234, 0.08) 100%) !important;
        border-color: rgba(102, 126, 234, 0.5) !important;
        color: white !important;
        transform: translateY(-3px) scale(1.01) !important;
        box-shadow: 
            0 8px 20px rgba(102, 126, 234, 0.25),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
    }

    /* Section questions */
    .questions-title {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 0.7rem;
        margin-top: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.12) !important;
        margin: 1rem 0 !important;
    }
    
    /* Sidebar glassmorphism */
    [data-testid="stSidebar"] {
        background: rgba(10, 10, 26, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    [data-testid="stSidebar"] .block-container {
        padding: 2rem 1.5rem !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Scrollbar personnalisée */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.3);
        border-radius: 10px;
        border: 2px solid transparent;
        background-clip: padding-box;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(102, 126, 234, 0.5);
        border-radius: 10px;
        background-clip: padding-box;
    }
</style>
""", unsafe_allow_html=True)

# Injecter le composant 3D Terre (le script monte le canvas dans le parent)
st.components.v1.html(EARTH_3D_COMPONENT, height=1, scrolling=False)

# Layout principal - Chat à gauche (40%), Planète à droite (60%)
col_chat, col_space = st.columns([0.9, 1.5])

with col_chat:
    # Utiliser un conteneur Streamlit natif
    chat_container = st.container()
    
    with chat_container:

        
        # Questions prédéfinies - liste verticale
        # Utilisation de &nbsp; (espace insécable) pour éviter les orphelins
        PREDEFINED_QUESTIONS = [
            "🎓 Quel est ton parcours\u00A0académique\u00A0?",
            "💼 Quelles sont tes expériences\u00A0professionnelles\u00A0?",
            "🛠️ Quelles sont tes compétences\u00A0techniques\u00A0?",
            "🚀 Parle-moi de tes\u00A0projets",
            "📧 Comment te\u00A0contacter\u00A0?",
            "🌟 Qu'est-ce qui te\u00A0passionne\u00A0?",
        ]
        
        # Initialisation de l'état
        if "selected_question" not in st.session_state:
            st.session_state.selected_question = None
        
        def handle_question_click(question):
            st.session_state.selected_question = question
        
        # Afficher les questions prédéfinies en layout vertical
        if "messages" not in st.session_state or len(st.session_state.get("messages", [])) <= 1:
            st.markdown('<p class="questions-title">💡 Questions suggérées</p>', unsafe_allow_html=True)
            
            # Layout vertical - 1 colonne
            for i, question in enumerate(PREDEFINED_QUESTIONS):
                if st.button(question, key=f"q_{i}", use_container_width=True):
                    handle_question_click(question)
            
            st.divider()
        
        # Avatar pour l'assistant
        ASSISTANT_AVATAR = "assets/assistant_avatar.png"
        
        # Initialisation de l'historique des messages
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "👋 Bonjour ! Je suis Elliot Feroux, étudiant en BUT Science des Données. "
                               "N'hésitez pas à me poser vos questions sur mon parcours, mes compétences ou mes projets !"
                }
            ]
        
        # Affichage de l'historique des messages
        for message in st.session_state.messages:
            avatar = ASSISTANT_AVATAR if message["role"] == "assistant" else None
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])
        
        # Déterminer la question à traiter
        prompt = None
        
        if st.session_state.selected_question:
            prompt = st.session_state.selected_question
            st.session_state.selected_question = None
        
        if user_input := st.chat_input("Posez votre question..."):
            prompt = user_input
        
        # Traiter la question
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
                with st.spinner("Je réfléchis..."):
                    try:
                        agent = get_agent()
                        result = Runner.run_sync(agent, prompt)
                        response = result.final_output
                    except Exception as e:
                        response = f"❌ Une erreur s'est produite : {str(e)}"
                
                st.markdown(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

# Sidebar
with st.sidebar:
    st.markdown("### 🌍 Navigation")
    st.markdown("Faites glisser la Terre avec votre souris pour explorer !")
    
    st.divider()
    
    st.markdown("### 📌 À propos")
    st.markdown(
        "Portfolio alimenté par **RAG** et **IA** pour répondre à vos questions."
    )
    
    st.divider()
    
    st.markdown("### 🔧 Technologies")
    st.markdown("• Python & Streamlit")
    st.markdown("• OpenAI Agents")
    st.markdown("• Three.js (3D)")
    
    st.divider()
    
    if st.button("🗑️ Effacer l'historique", use_container_width=True):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()
