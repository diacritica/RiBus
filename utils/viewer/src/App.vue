<script setup>
import { ref } from 'vue'
import { VMap, VMapOsmTileLayer, VMapZoomControl } from 'vue-map-ui'
import GeoJSON from './components/GeoJSON.vue'

const center = ref({
  lat: 40.35306192891293,
  lng: -3.5252388696140207
})
const zoom = ref(14)

function onViewChanged(e) {
  // console.log(e)
  // NOOP
}
</script>

<template>
  <VMap class="map" ref="containerComponent" :center="center" :zoom="zoom" @view-changed="onViewChanged">
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
