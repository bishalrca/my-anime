// Number of episodes from the html
const episodes = document.getElementsByClassName("episodes");
const episodeArray = Array.from(episodes);

// Split the episodes into chunks of 100
const chunkArray = [];
const chunks = 100;
for (let i = 0; i < episodeArray.length; i += chunks) {
  let tempArray = episodeArray.slice(i, i + chunks);
  chunkArray.push(tempArray);
}

// Create the pagination with the number of pages
const pages = chunkArray.length;
for (let i = 0; i < pages; i++) {
  const page = document.createElement("li");
  page.innerHTML = `<a class="page-link focus:bg-orange-500 relative block py-1.5 rounded-xl bg-[#18191A] px-4 cursor-pointer border-0 bg-transparent outline-none transition-all duration-300 rounded hover:text-orange-500 hover:bg-gray-200 focus:shadow-none">${
    i + 1
  }</a>`;
  document.getElementsByClassName("page-item-number")[0].appendChild(page);
}

// Add the event listener to the pagination
for (let i = 0; i < pages; i++) {
  const page =
    document.getElementsByClassName("page-item-number")[0].children[i];
  page.addEventListener("click", () => {
    const episodeContainer = document.getElementsByClassName("grid")[0];
    episodeContainer.innerHTML = "";
    for (let j = 0; j < chunkArray[i].length; j++) {
      episodeContainer.appendChild(chunkArray[i][j]);
    }
  });
}

// On first load, show the first 100 episodes
const episodeContainer = document.getElementsByClassName("grid")[0];
episodeContainer.innerHTML = "";
for (let j = 0; j < chunkArray[0].length; j++) {
  episodeContainer.appendChild(chunkArray[0][j]);
}
