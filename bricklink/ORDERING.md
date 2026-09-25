# Ordering the parts on BrickLink

Everything you need to buy for **Nobles & Common Folk at Quarrel** is in this folder:

| File | What it is |
|---|---|
| `wanted_list_complete.xml` | The whole set: **3,528 pieces in 293 lots** (26 minifigures, 4 horses, 4 baseplates) |
| `wanted_list_book1_lionhold.xml` | Book 1 only: Lionhold castle (1,263 pieces) |
| `wanted_list_book2_millbrook.xml` | Book 2 only: Millbrook village (872 pieces) |
| `wanted_list_book3_ravencrag.xml` | Book 3 only: Ravencrag Keep (1,094 pieces) |
| `wanted_list_book4_warriors.xml` | Book 4 only: minifigures, horses and catapults (299 pieces) |
| `parts_list.csv` | Spreadsheet of every lot: BrickLink ID, colour, quantity per book, estimated price and notes |
| `budget_summary.json` | The numbers below, machine-readable |

## Budget

| Book | Pieces | Lots | Estimated parts cost |
|---|---:|---:|---:|
| 1 · Lionhold | 1,263 | 60 | $118.63 |
| 2 · Millbrook | 872 | 114 | $108.37 |
| 3 · Ravencrag Keep | 1,094 | 76 | $113.33 |
| 4 · Warriors & Weapons | 299 | 110 | $89.30 |
| **Complete set** | **3,528** | **293** | **$429.64** |

The estimates use typical BrickLink per-piece prices (USD, a mix of new and used) and are meant for
budgeting only. Real prices depend on the sellers you pick, condition and where you live, and
**shipping is not included**. Expect roughly $20–45 of shipping when the order is split across 3–6
shops. That leaves the target of about $500 within reach. The four biggest cost drivers are:

* 1,331 light and dark bluish grey 1×2 / 1×4 wall bricks, masonry bricks included (about $95)
* 4 green 32×32 baseplates (about $26)
* 4 horses (about $18)
* 32 arched windows with diamond lattice panes (about $21)

## How to upload and buy

1. Log in to bricklink.com and go to **Want → Upload** (bricklink.com/v2/wanted/upload.page).
2. Open `wanted_list_complete.xml` in a text editor, copy everything and paste it into the upload box
   (or use the file picker). Choose **Create new Wanted List** and name it *Nobles & Common Folk*.
3. Press **Verify**. BrickLink shows every item it recognised. If an item is rejected, look it up in
   `parts_list.csv`; the *Note* column gives an alternative.
4. Press **Proceed to upload**.
5. Open the new Wanted List and press **Buy All**. In the Buy All settings choose
   *condition: any*, *minimise the number of shops*, and your shipping country. Easy Buy then proposes
   a set of shops. Check the proposed total against the budget above before you checkout.

Tip: to spread the cost, upload one book at a time (`wanted_list_book1_lionhold.xml` first) and build
it before buying the next.

## Items worth a second look

These lots are older, rarer or harder to find. Each one has a drop-in substitute:

| Item | Colour | Qty | If you can't find it |
|---|---|---:|---|
| Roof slopes 3037, 3039, 3045, 3688 | Dark Blue | 73 | Use **Blue** or **Black** for all of Ravencrag's roofs (swap them all together so the roofs match) |
| Horse barding 2490 | Red, Black | 2 + 2 | Optional decoration; the knights work without it |
| Flag 4 × 1 wave 4495b | Dark Blue, Red, Yellow | 12 | Any 4 × 1 wave flag (4495a/4495b) or a 2 × 2 flag on a bar |
| Minifig cape 4524 | Black | 2 | A cloth cape (item 522) |
| Minifig torso 973 + arms 981/982 + hands 983 | various | 26 | Many shops sell plain torsos already assembled with arms and hands; either is fine |
| Helmet 4503 | Flat Silver | 2 | Light Bluish Grey |
| Ridge 3043 | Dark Red | 12 | Red |
| Small pine 2435 | Dark Green | 2 | Green |

## Colour notes

* All colour IDs in the XML are BrickLink colour IDs (for example 86 = Light Bluish Gray,
  85 = Dark Bluish Gray, 88 = Reddish Brown, 63 = Dark Blue).
* Castle walls mix plain bricks with *Brick 1 × 2 with masonry profile* (98283) for texture. If
  98283 is expensive where you are, plain 1 × 2 bricks (3004) in the same colour build the same wall.
* The random dark grey and black bricks in the walls are weathering. Any mix of the two greys works.
