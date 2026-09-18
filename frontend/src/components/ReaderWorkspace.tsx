import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  ActionIcon,
  Alert,
  Badge,
  Box,
  Button,
  Card,
  Divider,
  Group,
  Paper,
  Progress,
  RingProgress,
  Select,
  SimpleGrid,
  Stack,
  Text,
  Title,
  Tooltip,
} from '@mantine/core';
import { notifications } from '@mantine/notifications';
import {
  IconArrowDown,
  IconBrain,
  IconClockPlay,
  IconClockPause,
  IconGauge,
  IconRefresh,
  IconTargetArrow,
} from '@tabler/icons-react';

import type { AccessibilitySettings, ReadingBlock, ThemePalette, TransformationResponse } from '../types';
import { isAnchorVerified } from '../utils/anchor';
import { prefersReducedMotion } from '../utils/feedback';
import { NuanceAlert } from './NuanceAlert';
import { ReadingBlockCard } from './ReadingBlockCard';

interface Props {
  data: TransformationResponse;
  sourceText: string;
  settings: AccessibilitySettings;
  palette: ThemePalette;
  onInspectSource: (block: ReadingBlock) => void;
  onProgress: (percent: number) => void;
}

const difficultyColour = (score: number): string =>
  score >= 8 ? 'red' : score >= 6 ? 'orange' : 'teal';

export const ReaderWorkspace: React.FC<Props> = ({
  data,
  sourceText,
  settings,
  palette,
  onInspectSource,
  onProgress,
}) => {
  const [readBlocks, setReadBlocks] = useState<Set<number>>(new Set());
  const [activeIndex, setActiveIndex] = useState<number>(0);
  const [secondsRemaining, setSecondsRemaining] = useState<number>(
    data.blocks[0]?.estimated_reading_seconds ?? 45
  );
  const [pacerRunning, setPacerRunning] = useState<boolean>(false);
  const intervalRef = useRef<number | null>(null);

  const activeBlock = data.blocks[activeIndex];

  const verifiedMap = useMemo(() => {
    const map = new Map<number, boolean>();
    data.blocks.forEach((block) => {
      map.set(block.block_id, isAnchorVerified(sourceText, block.source_citation_anchor));
    });
    return map;
  }, [data.blocks, sourceText]);

  const unverifiedCount = useMemo(
    () => Array.from(verifiedMap.values()).filter((verified) => !verified).length,
    [verifiedMap]
  );

  const quizCount = useMemo(
    () => data.blocks.filter((block) => Boolean(block.quiz)).length,
    [data.blocks]
  );

  const progress = (readBlocks.size / data.blocks.length) * 100;

  useEffect(() => {
    onProgress(progress);
  }, [progress, onProgress]);

  useEffect(() => {
    setSecondsRemaining(activeBlock?.estimated_reading_seconds ?? 45);
  }, [activeBlock]);

  const scrollToBlock = useCallback((index: number) => {
    const block = data.blocks[index];
    if (!block) return;
    const element = document.getElementById(`cognita-block-${block.block_id}`);
    element?.scrollIntoView({
      behavior: prefersReducedMotion() ? 'auto' : 'smooth',
      block: 'start',
    });
  }, [data.blocks]);

  const markRead = useCallback((blockId: number, read: boolean) => {
    setReadBlocks((previous) => {
      const next = new Set(previous);
      if (read) next.add(blockId);
      else next.delete(blockId);
      return next;
    });
  }, []);

  const toggleRead = useCallback(
    (blockId: number) => {
      setReadBlocks((previous) => {
        const next = new Set(previous);
        if (next.has(blockId)) next.delete(blockId);
        else next.add(blockId);
        return next;
      });
    },
    []
  );

  const goToNextBlock = useCallback(() => {
    if (activeIndex >= data.blocks.length - 1) {
      setPacerRunning(false);
      notifications.show({
        title: 'Document complete',
        message: 'Every focus sprint has been cleared. Nice sustained attention.',
        color: 'teal',
      });
      return;
    }
    const nextIndex = activeIndex + 1;
    setActiveIndex(nextIndex);
    setPacerRunning(false);
    window.setTimeout(() => scrollToBlock(nextIndex), 60);
  }, [activeIndex, data.blocks.length, scrollToBlock]);

  // Sprint countdown
  useEffect(() => {
    if (!pacerRunning) {
      if (intervalRef.current !== null) {
        window.clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    intervalRef.current = window.setInterval(() => {
      setSecondsRemaining((previous) => {
        if (previous <= 1) {
          setPacerRunning(false);
          if (activeBlock) markRead(activeBlock.block_id, true);
          notifications.show({
            title: `Sprint ${activeBlock ? activeBlock.block_id : ''} cleared`,
            message: 'Checkpoint reached — take a 20 second reset or continue.',
            color: 'indigo',
          });
          return 0;
        }
        return previous - 1;
      });
    }, 1000);

    return () => {
      if (intervalRef.current !== null) {
        window.clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [pacerRunning, activeBlock, markRead]);

  const sprintTotal = activeBlock?.estimated_reading_seconds ?? 1;
  const sprintElapsedPercent = ((sprintTotal - secondsRemaining) / sprintTotal) * 100;

  const handleQuizAnswered = (_blockId: number, correct: boolean) => {
    if (correct) {
      notifications.show({
        title: 'Retrieval checkpoint passed',
        message: 'That concept is now more likely to stick. Keep going.',
        color: 'teal',
        autoClose: 2600,
      });
    }
  };

  const jumpOptions = data.blocks.map((block, index) => ({
    value: String(index),
    label: `Block ${block.block_id} · ${block.headline.slice(0, 46)}`,
  }));

  return (
    <Box className="cognita-workspace">
      <Stack gap="lg">
        {/* Executive overview ----------------------------------------- */}
        <Card
          withBorder
          radius="md"
          padding="lg"
          style={{ backgroundColor: palette.surface, borderColor: palette.border }}
        >
          <Group justify="space-between" align="flex-start" wrap="wrap" mb="sm">
            <Box style={{ flex: 1, minWidth: 240 }}>
              <Title order={2} size="h3" mb={6}>
                {data.document_title}
              </Title>
              <Group gap="xs" wrap="wrap">
                <Badge
                  color={difficultyColour(data.difficulty_score)}
                  variant="light"
                  leftSection={<IconGauge size={12} />}
                >
                  Difficulty {data.difficulty_score}/10
                </Badge>
                <Badge color="gray" variant="light" leftSection={<IconClockPlay size={12} />}>
                  ~{data.overall_read_time_minutes} min focused reading
                </Badge>
                <Badge color="indigo" variant="light">
                  {data.blocks.length} blocks
                </Badge>
                <Badge color="teal" variant="light" leftSection={<IconTargetArrow size={12} />}>
                  {quizCount} checkpoints
                </Badge>
                {unverifiedCount > 0 && (
                  <Badge color="orange" variant="light">
                    {unverifiedCount} unverified anchor{unverifiedCount === 1 ? '' : 's'}
                  </Badge>
                )}
              </Group>
            </Box>

            <RingProgress
              size={104}
              thickness={9}
              roundCaps
              sections={[
                { value: progress, color: 'teal' },
              ]}
              label={
                <Text ta="center" size="xs" fw={700}>
                  {Math.round(progress)}%
                  <br />
                  read
                </Text>
              }
            />
          </Group>

          <Divider my="sm" />

          <Group align="flex-start" gap="xs" wrap="nowrap">
            <IconBrain size={17} color={palette.accent} style={{ marginTop: 3 }} aria-hidden />
            <Text size="sm" style={{ flex: 1 }}>
              {data.executive_summary}
            </Text>
          </Group>
        </Card>

        <NuanceAlert caveats={data.nuance_caveats} />

        {/* Focus pacer ------------------------------------------------- */}
        <Paper
          withBorder
          radius="md"
          p="md"
          style={{
            backgroundColor: palette.surface,
            borderColor: palette.border,
            position: 'sticky',
            top: 8,
            zIndex: 200,
          }}
        >
          <Group justify="space-between" align="center" wrap="wrap" gap="sm">
            <Group gap="xs" wrap="nowrap">
              <ActionIcon
                size="lg"
                radius="xl"
                variant="filled"
                color={pacerRunning ? 'orange' : 'indigo'}
                onClick={() => setPacerRunning((running) => !running)}
                aria-label={pacerRunning ? 'Pause focus sprint' : 'Start focus sprint'}
              >
                {pacerRunning ? <IconClockPause size={18} /> : <IconClockPlay size={18} />}
              </ActionIcon>

              <Box>
                <Text size="xs" c={palette.mutedText} lh={1.2}>
                  Focus sprint · block {activeBlock?.block_id} of {data.blocks.length}
                </Text>
                <Text fw={600} size="sm" lh={1.3}>
                  {activeBlock?.headline}
                </Text>
              </Box>
            </Group>

            <Group gap="sm" wrap="nowrap">
              <Text
                fw={700}
                size="xl"
                style={{ fontVariantNumeric: 'tabular-nums', minWidth: 58 }}
                aria-live="polite"
                aria-label={`${secondsRemaining} seconds remaining in this sprint`}
              >
                {String(Math.floor(secondsRemaining / 60)).padStart(2, '0')}:
                {String(secondsRemaining % 60).padStart(2, '0')}
              </Text>

              <Progress
                value={sprintElapsedPercent}
                size="lg"
                radius="xl"
                color={pacerRunning ? 'indigo' : 'gray'}
                w={140}
                aria-label="Sprint elapsed progress"
              />

              <Tooltip label="Next block">
                <Button
                  size="xs"
                  variant="light"
                  color="indigo"
                  rightSection={<IconArrowDown size={14} />}
                  onClick={goToNextBlock}
                >
                  Continue
                </Button>
              </Tooltip>

              <Tooltip label="Reset sprint timer">
                <ActionIcon
                  variant="subtle"
                  color="gray"
                  onClick={() => {
                    setPacerRunning(false);
                    setSecondsRemaining(activeBlock?.estimated_reading_seconds ?? 45);
                  }}
                  aria-label="Reset sprint timer"
                >
                  <IconRefresh size={16} />
                </ActionIcon>
              </Tooltip>
            </Group>
          </Group>

          <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="sm" mt="sm">
            <Select
              size="xs"
              label="Jump to block"
              data={jumpOptions}
              value={String(activeIndex)}
              onChange={(value) => {
                if (value === null) return;
                const index = Number(value);
                setActiveIndex(index);
                setPacerRunning(false);
                window.setTimeout(() => scrollToBlock(index), 60);
              }}
              searchable
              comboboxProps={{ withinPortal: true }}
            />
            <Box>
              <Text size="xs" fw={500} mb={4}>
                Session progress
              </Text>
              <Progress value={progress} size="md" radius="xl" color="teal" />
              <Text size="xs" c={palette.mutedText} mt={4}>
                {readBlocks.size} of {data.blocks.length} blocks marked read
              </Text>
            </Box>
          </SimpleGrid>
        </Paper>

        {unverifiedCount > 0 && (
          <Alert color="orange" variant="light" title="Provenance warning">
            <Text size="xs">
              {unverifiedCount} block{unverifiedCount === 1 ? '' : 's'} cite an anchor that could
              not be matched verbatim in your source text. Open “Verify in original source” on
              those blocks and confirm the claim manually.
            </Text>
          </Alert>
        )}

        {/* Reading blocks --------------------------------------------- */}
        {data.blocks.map((block, index) => (
          <ReadingBlockCard
            key={block.block_id}
            block={block}
            settings={settings}
            palette={palette}
            anchorVerified={verifiedMap.get(block.block_id) ?? false}
            isActive={index === activeIndex}
            isRead={readBlocks.has(block.block_id)}
            onInspectSource={onInspectSource}
            onQuizAnswered={handleQuizAnswered}
            onToggleRead={toggleRead}
          />
        ))}

        <Group justify="center">
          <Button
            variant="light"
            color="teal"
            onClick={() => {
              setReadBlocks(new Set(data.blocks.map((block) => block.block_id)));
              notifications.show({
                title: 'Document marked complete',
                message: 'Revisit the nuance sentinel before your exam.',
                color: 'teal',
              });
            }}
          >
            Mark entire document as read
          </Button>
        </Group>
      </Stack>
    </Box>
  );
};
