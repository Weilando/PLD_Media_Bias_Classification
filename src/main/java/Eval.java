import java.util.Set;
import java.util.List;
import java.util.Arrays;
import java.io.File;
import java.io.IOException;
import java.util.stream.Collectors;
import org.apache.commons.io.FileUtils;

public class Eval {

	String DELIMITER = ",";	
	Set<String> gold_leftPlds;
	Set<String> gold_rightPlds;
	List<String> generated_leftPlds;
	List<String> generated_rightPlds;

	public Eval(String[] filenames) throws IOException {
		String filenameLeftPlds_gold = filenames[0];
		String filenameRightPlds_gold = filenames[1];
		String filenameLeftPlds = filenames[2];
		String filenameRightPlds = filenames[3];
		this.gold_leftPlds = FileUtils.readLines(new File(filenameLeftPlds_gold))
			.stream()
			.map(line -> line.split(DELIMITER)[0])
			.collect(Collectors.toSet());
		this.gold_rightPlds = FileUtils.readLines(new File(filenameRightPlds_gold))
			.stream()
			.map(line -> line.split(DELIMITER)[0])
			.collect(Collectors.toSet());
		this.generated_leftPlds = FileUtils.readLines(new File(filenameLeftPlds))
			.stream()
			.map(line -> line.split(DELIMITER)[0])
			.collect(Collectors.toList());
		this.generated_rightPlds = FileUtils.readLines(new File(filenameRightPlds))
			.stream()
			.map(line -> line.split(DELIMITER)[0])
			.collect(Collectors.toList());
	}

	public float getAccuracy() {
		int TP = getTruePositives();
		int TN = getTrueNegatives();
		int FP = getFalsePositives();
		int FN = getFalseNegatives();

		return (TP + TN) / Float.valueOf( TP + TN + FP + FN );
	}

	public int getTruePositives() {
		int sum_left = this.generated_leftPlds.stream()
			.filter(pld -> this.gold_leftPlds.contains(pld))
			.map(pld -> 1)
			.mapToInt(x -> x)
			.sum();
		int sum_right = this.generated_rightPlds.stream()
			.filter(pld -> this.gold_rightPlds.contains(pld))
			.map(pld -> 1)
			.mapToInt(x -> x)
			.sum();
		return sum_left + sum_right;
	}

	public int getFalsePositives() {
		 int sum_left = this.generated_leftPlds.stream()
			.filter(pld -> !this.gold_leftPlds.contains(pld))
			.map(pld -> 1)
			.mapToInt(x -> x)
			.sum();
		 int sum_right = this.generated_rightPlds.stream()
			.filter(pld -> !this.gold_rightPlds.contains(pld))
			.map(pld -> 1)
			.mapToInt(x -> x)
			.sum();
		 return sum_left + sum_right;
	}

	public int getTrueNegatives() {
		int sum_left = this.gold_rightPlds.stream()
			.filter(pld -> !this.generated_leftPlds.contains(pld))
			.map(pld -> 1)
			.mapToInt(x -> x)
			.sum();
		int sum_right = this.gold_leftPlds.stream()
			.filter(pld -> !this.generated_rightPlds.contains(pld))
			.map(pld -> 1)
			.mapToInt(x -> x)
			.sum();
		return sum_left + sum_right;
	}

	public int getFalseNegatives() {
		int sum_left = this.gold_rightPlds.stream()
			.filter(pld -> !this.generated_rightPlds.contains(pld))
			.map(pld -> 1)
			.mapToInt(x -> x)
			.sum();
		int sum_right = this.gold_leftPlds.stream()
			.filter(pld -> !this.generated_leftPlds.contains(pld))
			.map(pld -> 1)
			.mapToInt(x -> x)
			.sum();
		return sum_left + sum_right;
	}

        public static void main(String[] args) throws IOException {
                Eval e = new Eval(Arrays.stream(new String[] {
                        "gold_left.csv",
                        "gold_right.csv",
                        "generated_left.csv",
                        "generated_right.csv"})
                                .map(filename ->
                                        Eval.class
                                        .getClassLoader()
                                        .getResource(filename)
                                        .getFile())
                                .toArray(String[]::new));
                System.out.println(e.getAccuracy());
        }

}
