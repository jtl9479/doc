package step01.item01;

public class StaticFactoryExample {

    private final boolean value;

    private StaticFactoryExample(boolean value) {
        this.value = value;
    }

    public static StaticFactoryExample valueOf(boolean value) {
        return value ? TRUE : FALSE;
    }

    private static final StaticFactoryExample TRUE = new StaticFactoryExample(true);
    private static final StaticFactoryExample FALSE = new StaticFactoryExample(false);

    @Override
    public String toString() {
        return "StaticFactoryExample{" + value + "}";
    }

    public static void main(String[] args) {
        StaticFactoryExample a = StaticFactoryExample.valueOf(true);
        StaticFactoryExample b = StaticFactoryExample.valueOf(true);
        System.out.println(a);
        System.out.println("동일 인스턴스 재사용? " + (a == b));
    }
}
