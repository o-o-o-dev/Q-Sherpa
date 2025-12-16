import type { Config } from "tailwindcss";

export default <Config>{
  corePlugins: {
    preflight: false, // Disables Tailwind's automatic reset
  },
};
