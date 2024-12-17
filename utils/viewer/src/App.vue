<script setup>
import { VMap, VMapOsmTileLayer, VMapZoomControl } from 'vue-map-ui';
import GeoJSON from './components/GeoJSON.vue';
</script>

<template>
  <VMap class="map" ref="containerComponent">
    <VMapOsmTileLayer />
    <GeoJSON url="/data/malla_media_epsg4326.geojson" />
    <GeoJSON url="/data/estudiantes_epsg4326.geojson" />
    <VMapZoomControl />
  </VMap>
</template>

<style scoped>
.map {
  width: 100%;
  height: 100%;
}
</style>
