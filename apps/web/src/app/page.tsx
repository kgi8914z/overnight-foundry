import { dashboardState } from "@/lib/load";
import { GuildHall } from "@/components/GuildHall";

export const dynamic = "force-dynamic";

export default function Page() {
  const state = dashboardState();
  return <GuildHall initial={state} />;
}
