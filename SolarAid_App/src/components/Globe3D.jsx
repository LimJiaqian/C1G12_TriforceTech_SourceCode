import React, { useRef, Suspense } from 'react';
import { Canvas, useFrame, useLoader } from '@react-three/fiber';
import * as THREE from 'three';

function EarthSphere() {
  const meshRef = useRef();
  const cloudsRef = useRef();

  // Load realistic Earth textures (NASA Blue Marble style)
  const earthTexture = useLoader(
    THREE.TextureLoader,
    'https://unpkg.com/three-globe@2.31.1/example/img/earth-blue-marble.jpg'
  );
  
  const bumpMap = useLoader(
    THREE.TextureLoader, 
    'https://unpkg.com/three-globe@2.31.1/example/img/earth-topology.png'
  );

  const cloudsTexture = useLoader(
    THREE.TextureLoader,
    'https://raw.githubusercontent.com/turban/webgl-earth/master/images/fair_clouds_4k.png'
  );

  // Slow, realistic rotation
  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.001;
    }
    if (cloudsRef.current) {
      cloudsRef.current.rotation.y += 0.0012;
    }
  });

  return (
    <group>
      {/* Earth with realistic Blue Marble texture */}
      <mesh ref={meshRef}>
        <sphereGeometry args={[3.5, 128, 128]} />
        <meshPhongMaterial 
          map={earthTexture}
          bumpMap={bumpMap}
          bumpScale={0.05}
          specular={new THREE.Color('#333333')}
          shininess={15}
        />
      </mesh>
      
      {/* Clouds layer - realistic white clouds */}
      <mesh ref={cloudsRef} scale={1.008}>
        <sphereGeometry args={[3.5, 128, 128]} />
        <meshPhongMaterial 
          map={cloudsTexture}
          transparent={true}
          opacity={0.8}
          depthWrite={false}
        />
      </mesh>
      
      {/* Subtle atmosphere glow */}
      <mesh scale={1.1}>
        <sphereGeometry args={[3.5, 64, 64]} />
        <meshBasicMaterial 
          color="#a8d5ff"
          transparent={true}
          opacity={0.1}
          side={THREE.BackSide}
        />
      </mesh>
    </group>
  );
}

export default function Globe3D() {
  return (
    <div style={{ width: '100%', height: '600px' }}>
      <Canvas 
        camera={{ position: [0, 0, 8], fov: 60 }}
      >
        <Suspense fallback={null}>
          {/* Bright lighting to show blue oceans */}
          <ambientLight intensity={1.2} />
          <directionalLight position={[5, 3, 5]} intensity={4.0} color="#ffffff" />
          <directionalLight position={[-3, -1, -3]} intensity={1.5} color="#e3f2fd" />
          <hemisphereLight skyColor="#ffffff" groundColor="#888888" intensity={0.8} />
          <EarthSphere />
        </Suspense>
      </Canvas>
    </div>
  );
}
