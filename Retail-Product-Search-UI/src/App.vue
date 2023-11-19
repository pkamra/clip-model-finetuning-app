<template>
  <div id="app">

    <div>
      <label for="productDescription">Enter Product Description:</label>
      <input type="text" id="productDescription" v-model="productDescription" />
      <button @click="fetchImages">Search</button>
    </div>


    <div v-if="images.length > 0">
      <h2>Images Received from API</h2>
      <div class="image-row" v-for="(row, index) in imageRows" :key="index">
        <div class="image-column" v-for="(image, imgIndex) in row" :key="imgIndex">
          <img :src="image" alt="Received Image" />
        </div>
      </div>
    </div>
    <div v-else>
      <p v-if="!isLoading && errorMessage">{{ errorMessage }}</p>
      <p v-if="isLoading">Loading...</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      images: [],
      isLoading: false,
      errorMessage: '',
      productDescription: '' // Added property to hold the product description
    };
  },
  computed: {
    imageRows() {
      const rows = [];
      for (let i = 0; i < this.images.length; i += 2) {
        rows.push(this.images.slice(i, i + 2));
      }
      return rows;
    }
  },
  methods: {
    async fetchImages() {
      this.isLoading = true;
      const apiUrl = 'http://localhost:8080/process_input';
      const headers = {
        'Content-Type': 'application/json'
      };
      const payload = {
        "input_data": this.productDescription // Use the entered product description
      };

      try {
        const response = await axios.post(apiUrl, payload, { headers: headers });
        const data = response.data;
        if (data.status === 'success') {
          this.images = data.results.image_data.map(imgData => `data:image/jpeg;base64,${imgData}`);
        } else {
          this.errorMessage = data.error_message || 'Unknown error occurred';
        }
      } catch (error) {
        this.errorMessage = 'Failed to fetch images';
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style>
.image-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
}

.image-column {
  flex: 0 0 calc(33.33% - 10px); /* Adjust the width of each column */
  margin: 5px;
}

.image-column img {
  width: 150px; /* Set the width of the images */
  height: auto; /* Maintain aspect ratio */
}
</style>

