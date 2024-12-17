<script setup>
import L from 'leaflet'
import { watch } from 'vue'
import { useMap } from 'vue-map-ui'
import { useFetch } from '@vueuse/core'

const props = defineProps({
  url: {
    type: String,
    required: true
  }
})

const map = useMap()
const { data } = useFetch(props.url).get().json()
watch(data, (geoJSON) => {
  L.geoJSON(geoJSON)
    .addTo(map.value)
})
</script>

<template>
  <div>Hola, Mundo!</div>
</template>
