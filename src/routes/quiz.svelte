<script>
    import { onMount } from 'svelte';

    let birds = [];

    onMount(async () => {
        const res = await fetch(`http://127.0.0.1:5000/api/random/ma/50`);
        birds = await res.json();
        console.log(birds);
    });
</script>

<main>
    <ul>
    {#each birds as bird}
        <li>
            {bird.common_name}
            <img src={bird.image} alt={bird.common_name} />
        </li>
    {/each}
    </ul>
</main>

<style>
img {
  display: block;
  margin-left: auto;
  margin-right: auto;
  min-width: 30vw;
  min-height: 30vh;
  max-width: 70vw;
  max-height: 70vh;
}
</style>