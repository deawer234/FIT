package ija.ija2020.homework1.store;

import ija.ija2020.homework1.goods.Goods;
import ija.ija2020.homework1.goods.GoodsItem;

public class StoreGoodsItem implements GoodsItem {

    @Override
    public Goods goods() {
        Goods goods1 = new StoreGoods("item");
        return null;
    }

    @Override
    public boolean sell() {
        return false;
    }
}
